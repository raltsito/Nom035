from collections import defaultdict

from django.db import transaction
from django.db.models import Avg, Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsTenantAdmin
from m00_onboarding.models import CicloNOM, Trabajador
from m00_onboarding.views import _muestra
from m05_questionnaires.models import Aplicacion
from .models import ResultadoAplicacion, ResultadoDominio, ResultadoDominioOficial
from .serializers import ResultadoAplicacionSerializer, ResultadoListSerializer
from .scoring import calcular_resultado


def _wrap(data, meta=None, errors=None, status_code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=status_code)


def _tenant_para_ciclo(request, ciclo_id):
    """Resuelve el tenant a consultar: para super admins, el del ciclo elegido
    (pueden operar sobre cualquier tenant); para tenant_admin, siempre el suyo."""
    if request.user.is_super_admin and ciclo_id:
        ciclo = CicloNOM.objects.filter(id=ciclo_id).select_related('tenant').first()
        return ciclo.tenant if ciclo else None
    return request.user.tenant


DIST_KEYS = ('nulo', 'bajo', 'medio', 'alto', 'muy_alto')


class ResultadoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsTenantAdmin,)

    def get_queryset(self):
        qs = ResultadoAplicacion.objects.select_related(
            'aplicacion__trabajador',
            'aplicacion__cuestionario',
            'aplicacion__ciclo',
        ).prefetch_related('dominios__dominio', 'dominios_oficiales')

        ciclo_id = self.request.query_params.get('ciclo_id')
        tenant   = _tenant_para_ciclo(self.request, ciclo_id)
        qs       = qs.filter(aplicacion__tenant=tenant)
        if ciclo_id:
            qs = qs.filter(aplicacion__ciclo_id=ciclo_id)

        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria=categoria)

        return qs.order_by(
            'aplicacion__trabajador__apellido_paterno',
            'aplicacion__trabajador__nombre',
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ResultadoAplicacionSerializer
        return ResultadoListSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = ResultadoListSerializer(qs, many=True)
        return _wrap(serializer.data, {'count': qs.count()})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return _wrap(ResultadoAplicacionSerializer(instance).data)

    # ------------------------------------------------------------------
    # POST /resultados/calcular/
    # ------------------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='calcular')
    @transaction.atomic
    def calcular(self, request):
        """Calcula (o recalcula) resultados para todas las aplicaciones completadas de un ciclo."""
        ciclo_id = request.data.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None,
                errors={'ciclo_id': ['Este campo es requerido.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        tenant = _tenant_para_ciclo(request, ciclo_id)
        try:
            ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
        except CicloNOM.DoesNotExist:
            return _wrap(None,
                errors={'ciclo_id': ['Ciclo no encontrado.']},
                status_code=status.HTTP_404_NOT_FOUND)

        aplicaciones = Aplicacion.objects.filter(
            tenant=tenant, ciclo=ciclo, estado='completado',
        ).select_related('cuestionario', 'trabajador').prefetch_related(
            'respuestas__pregunta',
            'cuestionario__dominios__preguntas',
        )

        if not aplicaciones.exists():
            return _wrap(None,
                errors={'detalle': ['No hay aplicaciones completadas en este ciclo.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        calculadas = actualizadas = omitidas = 0
        for aplicacion in aplicaciones:
            datos = calcular_resultado(aplicacion)
            if datos is None:
                ResultadoAplicacion.objects.filter(aplicacion=aplicacion).delete()
                omitidas += 1
                continue

            resultado, created = ResultadoAplicacion.objects.update_or_create(
                aplicacion=aplicacion,
                defaults={
                    'puntaje_total':     datos['puntaje_total'],
                    'puntaje_max':       datos['puntaje_max'],
                    'categoria':         datos['categoria'],
                    'requiere_atencion': datos.get('requiere_atencion'),
                },
            )

            resultado.dominios.all().delete()
            ResultadoDominio.objects.bulk_create([
                ResultadoDominio(
                    resultado   = resultado,
                    dominio_id  = d['dominio_id'],
                    puntaje     = d['puntaje'],
                    puntaje_max = d['puntaje_max'],
                    categoria   = d['categoria'],
                )
                for d in datos['dominios']
            ])

            resultado.dominios_oficiales.all().delete()
            ResultadoDominioOficial.objects.bulk_create([
                ResultadoDominioOficial(
                    resultado   = resultado,
                    clave       = d['clave'],
                    nombre      = d['nombre'],
                    orden       = d['orden'],
                    puntaje     = d['puntaje'],
                    puntaje_max = d['puntaje_max'],
                    categoria   = d['categoria'],
                )
                for d in datos.get('dominios_oficiales', [])
            ])

            if created:
                calculadas += 1
            else:
                actualizadas += 1

        return _wrap(None, meta={
            'ciclo_id':     ciclo.id,
            'ciclo_anio':   ciclo.anio,
            'calculadas':   calculadas,
            'actualizadas': actualizadas,
            'omitidas':     omitidas,
            'total':        calculadas + actualizadas,
        })

    # ------------------------------------------------------------------
    # GET /resultados/resumen/
    # ------------------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """Resumen agregado de resultados para un ciclo, desglosado por guía."""
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None,
                errors={'ciclo_id': ['Requerido.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        tenant = _tenant_para_ciclo(request, ciclo_id)
        qs_iii = self.get_queryset().filter(
            aplicacion__ciclo_id=ciclo_id,
            aplicacion__cuestionario__clave='III',
        )
        qs_i = self.get_queryset().filter(
            aplicacion__ciclo_id=ciclo_id,
            aplicacion__cuestionario__clave='I',
        )

        # Distribución global de Guía III
        dist_iii = {k: 0 for k in DIST_KEYS}
        for r in qs_iii:
            if r.categoria in dist_iii:
                dist_iii[r.categoria] += 1

        # Conteos de aplicaciones
        base = Aplicacion.objects.filter(tenant=tenant, ciclo_id=ciclo_id)
        total_apps       = base.count()
        total_completadas = base.filter(estado='completado').count()

        total_iii        = base.filter(cuestionario__clave='III').count()
        completadas_iii  = base.filter(cuestionario__clave='III', estado='completado').count()
        total_i          = base.filter(cuestionario__clave='I').count()
        completadas_i    = base.filter(cuestionario__clave='I', estado='completado').count()
        total_v          = base.filter(cuestionario__clave='V').count()
        completadas_v    = base.filter(cuestionario__clave='V', estado='completado').count()

        # Guía I: requieren atención
        requieren    = qs_i.filter(requiere_atencion=True).count()
        sin_indicadores = qs_i.filter(requiere_atencion=False).count()

        # HeadCount total y tamaño de muestra requerido (Ecuación 1, NOM-035-STPS-2018)
        headcount_total = Trabajador.objects.filter(tenant=tenant, activo=True).count()
        muestra_requerida = _muestra(headcount_total)

        # Empleados (no aplicaciones) que ya completaron TODAS sus guías asignadas en el ciclo
        por_trabajador = base.values('trabajador_id').annotate(
            total=Count('id'),
            completadas=Count('id', filter=Q(estado='completado')),
        )
        empleados_completos = sum(1 for row in por_trabajador if row['total'] == row['completadas'])

        return _wrap({
            'total_resultados':    qs_iii.count() + qs_i.count(),
            'total_completadas':   total_completadas,
            'total_aplicaciones':  total_apps,
            'headcount_total':     headcount_total,
            'muestra_requerida':   muestra_requerida,
            'empleados_completos': empleados_completos,
            'distribucion':        dist_iii,
            'guia_i': {
                'total':              total_i,
                'completadas':        completadas_i,
                'con_resultado':      qs_i.count(),
                'requieren_atencion': requieren,
                'sin_indicadores':    sin_indicadores,
            },
            'guia_iii': {
                'total':         total_iii,
                'completadas':   completadas_iii,
                'con_resultado': qs_iii.count(),
                'distribucion':  dist_iii,
            },
            'guia_v': {
                'total':       total_v,
                'completadas': completadas_v,
            },
        })

    # ------------------------------------------------------------------
    # GET /resultados/dominios-agregados/
    # ------------------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='dominios-agregados')
    def dominios_agregados(self, request):
        """
        Puntaje promedio, categoría modal y distribución de niveles por
        dominio oficial (Tabla 6, Guía III), incluyendo desglose por área.
        Solo considera dominios con puntaje_max > 0.
        """
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None,
                errors={'ciclo_id': ['Requerido.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        tenant = _tenant_para_ciclo(request, ciclo_id)

        dominios_qs = ResultadoDominioOficial.objects.filter(
            resultado__aplicacion__tenant=tenant,
            resultado__aplicacion__ciclo_id=ciclo_id,
            resultado__aplicacion__cuestionario__clave='III',
            puntaje_max__gt=0,
        ).select_related(
            'resultado__aplicacion__trabajador',
        )

        # Agrupar en memoria por clave de dominio
        dominio_map = {}
        for rd in dominios_qs:
            clave  = rd.clave
            nombre = rd.nombre
            area   = rd.resultado.aplicacion.trabajador.area or 'Sin área'

            if clave not in dominio_map:
                dominio_map[clave] = {
                    'dominio_clave':  clave,
                    'dominio_nombre': nombre,
                    'orden':          rd.orden,
                    'pt':             0,
                    'pm':             0,
                    'cats':           {k: 0 for k in DIST_KEYS},
                    'areas':          defaultdict(lambda: {'pt': 0, 'pm': 0, 'cats': {k: 0 for k in DIST_KEYS}}),
                }

            entry = dominio_map[clave]
            entry['pt'] += rd.puntaje
            entry['pm'] += rd.puntaje_max
            if rd.categoria in entry['cats']:
                entry['cats'][rd.categoria] += 1

            area_entry = entry['areas'][area]
            area_entry['pt'] += rd.puntaje
            area_entry['pm'] += rd.puntaje_max
            if rd.categoria in area_entry['cats']:
                area_entry['cats'][rd.categoria] += 1

        # Serializar resultado
        resultado = []
        for entry in sorted(dominio_map.values(), key=lambda x: x['orden']):
            pct_promedio = round(entry['pt'] / entry['pm'] * 100) if entry['pm'] else 0
            categoria_modal = max(entry['cats'], key=entry['cats'].get)

            por_area = {}
            for area_nombre, ae in entry['areas'].items():
                area_pct = round(ae['pt'] / ae['pm'] * 100) if ae['pm'] else 0
                area_cat = max(ae['cats'], key=ae['cats'].get)
                por_area[area_nombre] = {
                    'pct':      area_pct,
                    'categoria': area_cat,
                    'n':        sum(ae['cats'].values()),
                }

            resultado.append({
                'dominio_clave':    entry['dominio_clave'],
                'dominio_nombre':   entry['dominio_nombre'],
                'puntaje_promedio': round(entry['pt'] / max(sum(entry['cats'].values()), 1), 1),
                'pct_promedio':     pct_promedio,
                'categoria_modal':  categoria_modal,
                'distribucion':     entry['cats'],
                'por_area':         por_area,
            })

        return _wrap(resultado, {'total_dominios': len(resultado)})

    # ------------------------------------------------------------------
    # GET /resultados/ping/  — diagnóstico
    # ------------------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='ping')
    def ping(self, request):
        return _wrap({'ok': True, 'user': request.user.username})

    # ------------------------------------------------------------------
    # GET /resultados/atencion-clinica/
    # ------------------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='atencion-clinica')
    def atencion_clinica(self, request):
        """
        Lista de trabajadores de Guía I que requieren evaluación clínica.
        Incluye nombre, área y detalle de dominios positivos (acontecimiento y síntomas).
        """
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None,
                errors={'ciclo_id': ['Requerido.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        tenant = _tenant_para_ciclo(request, ciclo_id)
        qs = ResultadoAplicacion.objects.filter(
            aplicacion__tenant=tenant,
            aplicacion__ciclo_id=ciclo_id,
            aplicacion__cuestionario__clave='I',
            requiere_atencion=True,
        ).select_related(
            'aplicacion__trabajador',
        ).prefetch_related('dominios__dominio')

        data = []
        for resultado in qs:
            trabajador = resultado.aplicacion.trabajador

            dominios_detalle = []
            for rd in resultado.dominios.all():
                dominios_detalle.append({
                    'seccion':       rd.dominio.clave,
                    'nombre':        rd.dominio.nombre,
                    'positivos':     rd.puntaje,
                    'total':         rd.puntaje_max,
                })

            data.append({
                'resultado_id':     resultado.id,
                'trabajador_nombre': trabajador.nombre_completo,
                'trabajador_area':   trabajador.area or 'Sin área',
                'fecha_calculado':   resultado.calculado_en,
                'dominios':          dominios_detalle,
            })

        return _wrap(data, {'total': len(data)})
