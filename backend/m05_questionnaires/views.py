from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.decorators import permission_classes as deco_perms
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from accounts.permissions import IsTenantAdmin
from m00_onboarding.models import CicloNOM, Trabajador
from .models import Cuestionario, Aplicacion, RespuestaPregunta, Pregunta, GuiaLink
from .serializers import (
    CuestionarioSerializer, CuestionarioListSerializer,
    AplicacionSerializer, AplicacionPublicaSerializer,
    SubmitRespuestasSerializer,
    GuiaLinkSerializer, GuiaLinkPublicaSerializer,
)


def _wrap(data, meta=None, errors=None, status_code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=status_code)


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


_GUIA_PREVIA = {'III': 'V', 'I': 'III'}

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

    # Validación secuencial: V → III → I
    clave_actual = link.cuestionario.clave
    clave_previa = _GUIA_PREVIA.get(clave_actual)
    if clave_previa:
        completada = Aplicacion.objects.filter(
            tenant=link.ciclo.tenant,
            ciclo=link.ciclo,
            cuestionario__clave=clave_previa,
            trabajador=trabajador,
            estado='completado',
        ).exists()
        if not completada:
            return Response(
                {'data': None, 'meta': {}, 'errors': {
                    'bloqueado':      True,
                    'guia_requerida': clave_previa,
                    'mensaje':        f'Debes completar primero la Guía {clave_previa}.',
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
    total_preguntas = Pregunta.objects.filter(dominio__cuestionario=aplicacion.cuestionario).count()

    for item in respuestas_data:
        try:
            pregunta = Pregunta.objects.get(
                id=item['pregunta_id'], dominio__cuestionario=aplicacion.cuestionario)
        except Pregunta.DoesNotExist:
            continue
        RespuestaPregunta.objects.update_or_create(
            aplicacion=aplicacion, pregunta=pregunta,
            defaults={'valor': item['valor'], 'tenant': aplicacion.tenant},
        )

    respondidas = aplicacion.respuestas.count()
    if respondidas >= total_preguntas:
        aplicacion.marcar_completado()
    elif aplicacion.estado == 'pendiente':
        aplicacion.estado = 'en_progreso'
        aplicacion.save(update_fields=['estado'])

    return Response({'data': {
        'estado': aplicacion.estado,
        'respondidas': respondidas,
        'total': total_preguntas,
    }, 'meta': {}, 'errors': None})
