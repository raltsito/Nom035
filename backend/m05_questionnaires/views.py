import csv
import zipfile
from io import BytesIO
from xml.sax.saxutils import escape

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.decorators import permission_classes as deco_perms
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction

from accounts.permissions import IsTenantAdmin
from m00_onboarding.models import CicloNOM, Trabajador
from .models import Cuestionario, Aplicacion, RespuestaPregunta, Pregunta, GuiaLink
from .services import (
    GUIA_ORDEN,
    obtener_clave_guia_pendiente,
    obtener_clave_guia_pendiente_desde_completadas,
    obtener_claves_completadas_por_trabajador,
)
from .serializers import (
    CuestionarioSerializer, CuestionarioListSerializer,
    AplicacionSerializer, AplicacionPublicaSerializer,
    SubmitRespuestasSerializer,
    GuiaLinkSerializer, GuiaLinkPublicaSerializer,
)


def _wrap(data, meta=None, errors=None, status_code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=status_code)


def _pregunta_visible(pregunta, respuestas):
    condicion_ids = []
    if pregunta.condicion_pregunta_id:
        condicion_ids.append(pregunta.condicion_pregunta_id)
    if hasattr(pregunta, '_prefetched_objects_cache'):
        condicion_ids.extend(p.id for p in pregunta.condicion_preguntas.all())
    else:
        condicion_ids.extend(pregunta.condicion_preguntas.values_list('id', flat=True))

    if not condicion_ids:
        return True

    esperado = pregunta.condicion_valor
    checks = [respuestas.get(str(pid)) == esperado for pid in condicion_ids]
    if pregunta.condicion_operador == 'any':
        return any(checks)
    return all(checks)


class CuestionarioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Cuestionario.objects.prefetch_related('dominios__preguntas').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CuestionarioListSerializer
        return CuestionarioSerializer

    def list(self, request, *args, **kwargs):
        serializer = CuestionarioListSerializer(self.get_queryset(), many=True)
        return _wrap(serializer.data, {'count': self.get_queryset().count()})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return _wrap(CuestionarioSerializer(instance).data)


class AplicacionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class = AplicacionSerializer

    def get_queryset(self):
        qs = Aplicacion.objects.select_related(
            'trabajador', 'cuestionario', 'ciclo'
        ).prefetch_related('respuestas')

        ciclo_id = self.request.query_params.get('ciclo_id')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = AplicacionSerializer(qs, many=True)
        return _wrap(serializer.data, {'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return _wrap(AplicacionSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)

    def _get_progreso_export_rows(self, ciclo_id):
        tenant = self.request.user.tenant
        ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)

        aplicaciones = Aplicacion.objects.filter(
            tenant=tenant,
            ciclo=ciclo,
            cuestionario__clave__in=['V', 'III', 'I'],
        ).select_related('trabajador', 'cuestionario')

        idx = {}
        for apl in aplicaciones:
            tid = apl.trabajador_id
            if tid not in idx:
                idx[tid] = {}
            idx[tid][apl.cuestionario.clave] = apl.estado

        trabajadores = Trabajador.objects.filter(tenant=tenant, activo=True).order_by(
            'apellido_paterno', 'apellido_materno', 'nombre'
        )

        rows = []
        for trabajador in trabajadores:
            estados = idx.get(trabajador.id, {})
            rows.append({
                'num_empleado': trabajador.num_empleado,
                'nombre': trabajador.nombre_completo,
                'area': trabajador.area,
                'puesto': trabajador.puesto,
                'guia_V': estados.get('V', 'sin_iniciar'),
                'guia_III': estados.get('III', 'sin_iniciar'),
                'guia_I': estados.get('I', 'sin_iniciar'),
            })

        return ciclo, rows


    @action(detail=True, methods=['delete'], url_path='limpiar-respuestas')
    def limpiar_respuestas(self, request, pk=None):
        instance = self.get_object()
        instance.respuestas.all().delete()
        instance.estado = 'pendiente'
        instance.fecha_completado = None
        instance.save(update_fields=['estado', 'fecha_completado'])
        return _wrap(AplicacionSerializer(instance).data)

    @action(detail=False, methods=['get'], url_path='progreso')
    def progreso(self, request):
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None, errors={'ciclo_id': ['Este campo es requerido.']},
                         status_code=status.HTTP_400_BAD_REQUEST)

        tenant = request.user.tenant
        try:
            ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'ciclo_id': ['Ciclo no encontrado.']},
                         status_code=status.HTTP_404_NOT_FOUND)

        aplicaciones = Aplicacion.objects.filter(
            tenant=tenant,
            ciclo=ciclo,
            cuestionario__clave__in=['V', 'III', 'I'],
        ).select_related('trabajador', 'cuestionario')

        # índice: {trabajador_id: {clave: estado}}
        idx = {}
        for apl in aplicaciones:
            tid = apl.trabajador_id
            if tid not in idx:
                idx[tid] = {}
            idx[tid][apl.cuestionario.clave] = apl.estado

        trabajadores = Trabajador.objects.filter(tenant=tenant, activo=True).order_by(
            'apellido_paterno', 'apellido_materno', 'nombre'
        )

        result = []
        for t in trabajadores:
            p = idx.get(t.id, {})
            result.append({
                'trabajador_id':     t.id,
                'trabajador_nombre': t.nombre_completo,
                'trabajador_area':   t.area,
                'trabajador_puesto': t.puesto,
                'num_empleado':      t.num_empleado,
                'guia_V':            p.get('V'),
                'guia_III':          p.get('III'),
                'guia_I':            p.get('I'),
            })

        completados = sum(
            1 for r in result
            if r['guia_V'] == 'completado'
            and r['guia_III'] == 'completado'
            and r['guia_I'] == 'completado'
        )
        return _wrap(result, meta={
            'total': len(result),
            'completados_total': completados,
        })

    @action(detail=False, methods=['post'], url_path='enviar-correos-pendientes')
    def enviar_correos_pendientes(self, request):
        ciclo_id = request.query_params.get('ciclo_id') or request.data.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None, errors={'ciclo_id': ['Este campo es requerido.']},
                         status_code=status.HTTP_400_BAD_REQUEST)

        tenant = request.user.tenant
        try:
            ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'ciclo_id': ['Ciclo no encontrado.']},
                         status_code=status.HTTP_404_NOT_FOUND)

        trabajadores = list(
            Trabajador.objects.filter(tenant=tenant, activo=True).order_by(
                'apellido_paterno', 'apellido_materno', 'nombre'
            )
        )
        completadas_idx = obtener_claves_completadas_por_trabajador(
            ciclo,
            trabajadores=trabajadores,
            tenant=tenant,
        )
        links = {
            link.cuestionario.clave: link
            for link in GuiaLink.objects.filter(
                tenant=tenant,
                ciclo=ciclo,
                activo=True,
                cuestionario__clave__in=GUIA_ORDEN,
            ).select_related('cuestionario')
        }

        enviados = omitidos_sin_correo = omitidos_completos = omitidos_sin_link = errores_envio = 0
        detalle = []
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

        for trabajador in trabajadores:
            completadas = completadas_idx.get(trabajador.id, set())
            clave_pendiente = obtener_clave_guia_pendiente_desde_completadas(completadas)
            item = {
                'trabajador_id': trabajador.id,
                'trabajador': trabajador.nombre_completo,
                'correo': trabajador.email,
                'guia_enviada': clave_pendiente,
                'estado': '',
            }

            if clave_pendiente is None:
                omitidos_completos += 1
                item['estado'] = 'omitido_completo'
                detalle.append(item)
                continue

            if not trabajador.email:
                omitidos_sin_correo += 1
                item['estado'] = 'omitido_sin_correo'
                detalle.append(item)
                continue

            link = links.get(clave_pendiente)
            if not link:
                omitidos_sin_link += 1
                item['estado'] = 'omitido_sin_link'
                detalle.append(item)
                continue

            url = f'{frontend_url}/guia/{link.token}'
            item['link'] = url
            try:
                send_mail(
                    subject=f'Recordatorio NOM-035 - Guia {clave_pendiente} pendiente',
                    message=(
                        f'Hola {trabajador.nombre_completo},\n\n'
                        f'Tienes pendiente completar la Guia {clave_pendiente} del cuestionario NOM-035.\n\n'
                        f'Puedes responderla en el siguiente enlace:\n{url}\n\n'
                        'Gracias.'
                    ),
                    from_email=from_email,
                    recipient_list=[trabajador.email],
                    fail_silently=False,
                )
                enviados += 1
                item['estado'] = 'enviado'
            except Exception as exc:
                errores_envio += 1
                item['estado'] = 'error_envio'
                item['error'] = str(exc)
            detalle.append(item)

        return _wrap({
            'enviados': enviados,
            'omitidos_sin_correo': omitidos_sin_correo,
            'omitidos_completos': omitidos_completos,
            'omitidos_sin_link': omitidos_sin_link,
            'errores_envio': errores_envio,
            'detalle': detalle,
        }, meta={'total_trabajadores': len(trabajadores)})

    @action(detail=False, methods=['get'], url_path='exportar')
    def exportar(self, request):
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None, errors={'ciclo_id': ['Este campo es requerido.']},
                         status_code=status.HTTP_400_BAD_REQUEST)

        try:
            ciclo, rows = self._get_progreso_export_rows(ciclo_id)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'ciclo_id': ['Ciclo no encontrado.']},
                         status_code=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="aplicaciones_ciclo_{ciclo.id}.csv"'
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow(['num_empleado', 'nombre', 'area', 'puesto', 'guia_V', 'guia_III', 'guia_I'])

        for row in rows:
            writer.writerow([
                row['num_empleado'],
                row['nombre'],
                row['area'],
                row['puesto'],
                row['guia_V'],
                row['guia_III'],
                row['guia_I'],
            ])

        return response

    @action(detail=False, methods=['get'], url_path='exportar-excel')
    def exportar_excel(self, request):
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None, errors={'ciclo_id': ['Este campo es requerido.']},
                         status_code=status.HTTP_400_BAD_REQUEST)

        try:
            ciclo, rows = self._get_progreso_export_rows(ciclo_id)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'ciclo_id': ['Ciclo no encontrado.']},
                         status_code=status.HTTP_404_NOT_FOUND)

        estado_labels = {
            'completado': 'Completado',
            'en_progreso': 'En progreso',
            'pendiente': 'Pendiente',
            'sin_iniciar': 'Sin iniciar',
        }
        columns = ['No. empleado', 'Nombre', 'Área', 'Puesto', 'Guía V', 'Guía III', 'Guía I']
        col_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        widths = [16, 34, 22, 28, 16, 16, 16]

        def cell(ref, value, style=0):
            style_attr = f' s="{style}"' if style else ''
            return (
                f'<c r="{ref}" t="inlineStr"{style_attr}>'
                f'<is><t>{escape(str(value or ""))}</t></is>'
                '</c>'
            )

        sheet_rows = [
            '<row r="1" ht="24" customHeight="1">'
            f'{cell("A1", "Reporte de cuestionarios NOM-035", 5)}'
            '</row>',
            '<row r="2">'
            f'{cell("A2", f"Ciclo {ciclo}", 6)}'
            '</row>',
            '<row r="3">' + ''.join(
                cell(f'{letter}3', header, 1)
                for letter, header in zip(col_letters, columns)
            ) + '</row>',
        ]

        for index, row in enumerate(rows, start=4):
            values = [
                row['num_empleado'],
                row['nombre'],
                row['area'],
                row['puesto'],
                estado_labels[row['guia_V']],
                estado_labels[row['guia_III']],
                estado_labels[row['guia_I']],
            ]
            styles = [
                0, 0, 0, 0,
                {'completado': 2, 'en_progreso': 3, 'pendiente': 4, 'sin_iniciar': 7}[row['guia_V']],
                {'completado': 2, 'en_progreso': 3, 'pendiente': 4, 'sin_iniciar': 7}[row['guia_III']],
                {'completado': 2, 'en_progreso': 3, 'pendiente': 4, 'sin_iniciar': 7}[row['guia_I']],
            ]
            sheet_rows.append(
                f'<row r="{index}">' + ''.join(
                    cell(f'{letter}{index}', value, style)
                    for letter, value, style in zip(col_letters, values, styles)
                ) + '</row>'
            )

        last_row = max(len(rows) + 3, 3)
        cols_xml = ''.join(
            f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>'
            for idx, width in enumerate(widths, start=1)
        )
        sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="A1:G{last_row}"/>
  <sheetViews>
    <sheetView workbookViewId="0">
      <pane ySplit="3" topLeftCell="A4" activePane="bottomLeft" state="frozen"/>
      <selection pane="bottomLeft" activeCell="A4" sqref="A4"/>
    </sheetView>
  </sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <cols>{cols_xml}</cols>
  <sheetData>{''.join(sheet_rows)}</sheetData>
  <autoFilter ref="A3:G{last_row}"/>
  <mergeCells count="2">
    <mergeCell ref="A1:G1"/>
    <mergeCell ref="A2:G2"/>
  </mergeCells>
</worksheet>'''

        styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="4">
    <font><sz val="11"/><color rgb="FF1F2937"/><name val="Arial"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
    <font><b/><sz val="16"/><color rgb="FF1F2937"/><name val="Arial"/></font>
    <font><sz val="11"/><color rgb="FF6B7280"/><name val="Arial"/></font>
  </fonts>
  <fills count="7">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF1F2937"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFDCFCE7"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFDBEAFE"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFEF3C7"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF3F4F6"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFD1D5DB"/></left>
      <right style="thin"><color rgb="FFD1D5DB"/></right>
      <top style="thin"><color rgb="FFD1D5DB"/></top>
      <bottom style="thin"><color rgb="FFD1D5DB"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="8">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment horizontal="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment horizontal="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="5" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment horizontal="center"/></xf>
    <xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
    <xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>
    <xf numFmtId="0" fontId="0" fillId="6" borderId="1" xfId="0" applyFill="1" applyBorder="1"><alignment horizontal="center"/></xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''

        workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Progreso" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>'''
        workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
        root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>'''

        output = BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('[Content_Types].xml', content_types)
            archive.writestr('_rels/.rels', root_rels)
            archive.writestr('xl/workbook.xml', workbook_xml)
            archive.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
            archive.writestr('xl/styles.xml', styles_xml)
            archive.writestr('xl/worksheets/sheet1.xml', sheet_xml)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="aplicaciones_ciclo_{ciclo.id}.xlsx"'
        return response


class GuiaLinkViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class = GuiaLinkSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = GuiaLink.objects.select_related('cuestionario', 'ciclo')
        ciclo_id = self.request.query_params.get('ciclo_id')
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return _wrap(GuiaLinkSerializer(qs, many=True).data, {'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        return _wrap(GuiaLinkSerializer(self.get_object()).data)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return _wrap(None)

    @action(detail=False, methods=['post'], url_path='crear-links')
    @transaction.atomic
    def crear_links(self, request):
        ciclo_id = request.data.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None, errors={'ciclo_id': ['Este campo es requerido.']},
                         status_code=status.HTTP_400_BAD_REQUEST)

        tenant = request.user.tenant
        try:
            ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
        except CicloNOM.DoesNotExist:
            return _wrap(None, errors={'ciclo_id': ['Ciclo no encontrado.']},
                         status_code=status.HTTP_404_NOT_FOUND)

        cuestionarios = Cuestionario.objects.filter(clave__in=['V', 'III', 'I'])
        if cuestionarios.count() < 3:
            return _wrap(None,
                errors={'cuestionarios': ['Faltan guias. Ejecuta seed_cuestionarios.']},
                status_code=status.HTTP_404_NOT_FOUND)

        links = []
        creados = existentes = 0
        for c in cuestionarios:
            link, created = GuiaLink.objects.get_or_create(
                ciclo=ciclo, cuestionario=c,
                defaults={'tenant': tenant},
            )
            links.append(link)
            if created:
                creados += 1
            else:
                existentes += 1

        return _wrap(
            GuiaLinkSerializer(links, many=True).data,
            meta={'creados': creados, 'ya_existian': existentes},
            status_code=status.HTTP_201_CREATED,
        )


@api_view(['GET'])
@deco_perms([AllowAny])
def guia_link_publica(request, token):
    link = get_object_or_404(GuiaLink, token=token, activo=True)
    return Response({'data': GuiaLinkPublicaSerializer(link).data, 'meta': {}, 'errors': None})


@api_view(['POST'])
@deco_perms([AllowAny])
def identificar_trabajador(request, token):
    link = get_object_or_404(GuiaLink, token=token, activo=True)
    num_empleado = str(request.data.get('num_empleado', '')).strip()

    if not num_empleado:
        return Response(
            {'data': None, 'meta': {}, 'errors': {'num_empleado': ['Este campo es requerido.']}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        trabajador = Trabajador.objects.get(
            tenant=link.ciclo.tenant,
            num_empleado=num_empleado,
            activo=True,
        )
    except Trabajador.DoesNotExist:
        return Response(
            {'data': None, 'meta': {}, 'errors': {'num_empleado': ['Número de trabajador no encontrado.']}},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({'data': {
        'trabajador_id':   trabajador.id,
        'nombre_completo': trabajador.nombre_completo,
        'num_empleado':    trabajador.num_empleado,
        'puesto':          trabajador.puesto,
    }, 'meta': {}, 'errors': None})


@api_view(['POST'])
@deco_perms([AllowAny])
@transaction.atomic
def confirmar_trabajador(request, token):
    link = get_object_or_404(GuiaLink, token=token, activo=True)
    trabajador_id = request.data.get('trabajador_id')

    if not trabajador_id:
        return Response(
            {'data': None, 'meta': {}, 'errors': {'trabajador_id': ['Este campo es requerido.']}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        trabajador = Trabajador.objects.get(
            id=trabajador_id,
            tenant=link.ciclo.tenant,
            activo=True,
        )
    except Trabajador.DoesNotExist:
        return Response(
            {'data': None, 'meta': {}, 'errors': {'trabajador_id': ['Trabajador no válido.']}},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Validación secuencial: V -> III -> I
    clave_actual = link.cuestionario.clave
    clave_pendiente = obtener_clave_guia_pendiente(trabajador, link.ciclo)
    if (
        clave_pendiente
        and clave_actual in GUIA_ORDEN
        and GUIA_ORDEN.index(clave_actual) > GUIA_ORDEN.index(clave_pendiente)
    ):
        return Response(
            {'data': None, 'meta': {}, 'errors': {
                'bloqueado':      True,
                'guia_requerida': clave_pendiente,
                'mensaje':        f'Debes completar primero la Guia {clave_pendiente}.',
            }},
            status=status.HTTP_403_FORBIDDEN,
        )

    aplicacion, _ = Aplicacion.objects.get_or_create(
        tenant=link.ciclo.tenant,
        ciclo=link.ciclo,
        cuestionario=link.cuestionario,
        trabajador=trabajador,
    )

    return Response({'data': {
        'aplicacion_token': str(aplicacion.token),
    }, 'meta': {}, 'errors': None})


@api_view(['GET'])
@deco_perms([AllowAny])
def aplicacion_publica(request, token):
    aplicacion = get_object_or_404(Aplicacion, token=token)
    return Response({'data': AplicacionPublicaSerializer(aplicacion).data, 'meta': {}, 'errors': None})


@api_view(['POST'])
@deco_perms([AllowAny])
@transaction.atomic
def responder_aplicacion(request, token):
    aplicacion = get_object_or_404(Aplicacion, token=token)

    if aplicacion.estado == 'completado':
        return Response(
            {'data': None, 'meta': {}, 'errors': {'detalle': 'Este cuestionario ya fue completado.'}},
            status=status.HTTP_400_BAD_REQUEST)

    serializer = SubmitRespuestasSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'data': None, 'meta': {}, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    respuestas_data = serializer.validated_data['respuestas']
    preguntas = list(Pregunta.objects.filter(
        dominio__cuestionario=aplicacion.cuestionario
    ).select_related('condicion_pregunta').prefetch_related('condicion_preguntas'))
    preguntas_by_id = {p.id: p for p in preguntas}
    respuestas_actuales = {str(r.pregunta_id): r.valor for r in aplicacion.respuestas.all()}
    respuestas_entrantes = {}
    for item in respuestas_data:
        if 'valor' in item:
            respuestas_entrantes[str(item['pregunta_id'])] = item['valor']
        elif 'valor_texto' in item:
            respuestas_entrantes[str(item['pregunta_id'])] = item['valor_texto']
    respuestas_visibilidad = {**respuestas_actuales, **respuestas_entrantes}
    preguntas_visibles = [
        p for p in preguntas
        if _pregunta_visible(p, respuestas_visibilidad)
    ]
    preguntas_visibles_ids = {p.id for p in preguntas_visibles}

    for item in respuestas_data:
        pregunta = preguntas_by_id.get(item['pregunta_id'])
        if not pregunta or pregunta.id not in preguntas_visibles_ids:
            continue
        valor = item.get('valor')
        valor_texto = str(item.get('valor_texto', '')).strip()
        if pregunta.tipo_respuesta == 'si_no' and valor not in (0, 1):
            return Response(
                {'data': None, 'meta': {}, 'errors': {'valor': 'Las preguntas Si/No aceptan valores 0 o 1.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if pregunta.tipo_respuesta == 'frecuencia' and valor not in range(5):
            return Response(
                {'data': None, 'meta': {}, 'errors': {'valor': 'Las preguntas de frecuencia aceptan valores entre 0 y 4.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if pregunta.tipo_respuesta in ('texto', 'opcion') and not valor_texto:
            return Response(
                {'data': None, 'meta': {}, 'errors': {'valor_texto': 'Este campo es requerido.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if pregunta.tipo_respuesta == 'opcion' and valor_texto not in pregunta.opciones:
            return Response(
                {'data': None, 'meta': {}, 'errors': {'valor_texto': 'Opcion no valida.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        RespuestaPregunta.objects.update_or_create(
            aplicacion=aplicacion, pregunta=pregunta,
            defaults={
                'valor': valor if pregunta.tipo_respuesta in ('frecuencia', 'si_no') else None,
                'valor_texto': '' if pregunta.tipo_respuesta in ('frecuencia', 'si_no') else valor_texto,
                'tenant': aplicacion.tenant,
            },
        )

    respuestas_guardadas = {str(r.pregunta_id): r.valor for r in aplicacion.respuestas.all()}
    total_preguntas = len(preguntas_visibles)
    respondidas = sum(
        1 for p in preguntas_visibles
        if str(p.id) in respuestas_guardadas
    )
    if total_preguntas and respondidas >= total_preguntas:
        aplicacion.marcar_completado()
    elif aplicacion.estado == 'pendiente':
        aplicacion.estado = 'en_progreso'
        aplicacion.save(update_fields=['estado'])

    siguiente_guia_token = None
    if aplicacion.estado == 'completado':
        clave_actual = aplicacion.cuestionario.clave
        if clave_actual in GUIA_ORDEN:
            idx = GUIA_ORDEN.index(clave_actual)
            if idx + 1 < len(GUIA_ORDEN):
                siguiente_clave = GUIA_ORDEN[idx + 1]
                siguiente_link = GuiaLink.objects.filter(
                    tenant=aplicacion.tenant,
                    ciclo=aplicacion.ciclo,
                    cuestionario__clave=siguiente_clave,
                    activo=True,
                ).first()
                if siguiente_link:
                    siguiente_guia_token = str(siguiente_link.token)

    return Response({'data': {
        'estado': aplicacion.estado,
        'respondidas': respondidas,
        'total': total_preguntas,
        'siguiente_guia_token': siguiente_guia_token,
    }, 'meta': {}, 'errors': None})
