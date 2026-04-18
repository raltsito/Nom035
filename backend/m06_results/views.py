from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from accounts.permissions import IsTenantAdmin
from m00_onboarding.models import CicloNOM
from m05_questionnaires.models import Aplicacion
from .models import ResultadoAplicacion, ResultadoDominio
from .serializers import ResultadoAplicacionSerializer, ResultadoListSerializer
from .scoring import calcular_resultado


def _wrap(data, meta=None, errors=None, status_code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=status_code)


class ResultadoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsTenantAdmin,)

    def get_queryset(self):
        qs = ResultadoAplicacion.objects.select_related(
            'aplicacion__trabajador',
            'aplicacion__cuestionario',
            'aplicacion__ciclo',
        ).prefetch_related('dominios__dominio')

        # Filtrar por tenant via aplicacion
        tenant = self.request.user.tenant
        qs = qs.filter(aplicacion__tenant=tenant)

        ciclo_id = self.request.query_params.get('ciclo_id')
        if ciclo_id:
            qs = qs.filter(aplicacion__ciclo_id=ciclo_id)

        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria=categoria)

        return qs.order_by('aplicacion__trabajador__apellido_paterno',
                           'aplicacion__trabajador__nombre')

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

    @action(detail=False, methods=['post'], url_path='calcular')
    @transaction.atomic
    def calcular(self, request):
        """
        Calcula (o recalcula) resultados para todas las aplicaciones
        completadas de un ciclo. Idempotente.
        """
        ciclo_id = request.data.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None,
                errors={'ciclo_id': ['Este campo es requerido.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        tenant = request.user.tenant
        try:
            ciclo = CicloNOM.objects.get(id=ciclo_id, tenant=tenant)
        except CicloNOM.DoesNotExist:
            return _wrap(None,
                errors={'ciclo_id': ['Ciclo no encontrado.']},
                status_code=status.HTTP_404_NOT_FOUND)

        aplicaciones = Aplicacion.objects.filter(
            tenant=tenant,
            ciclo=ciclo,
            estado='completado',
        ).select_related('cuestionario', 'trabajador').prefetch_related(
            'respuestas__pregunta',
            'cuestionario__dominios__preguntas',
        )

        if not aplicaciones.exists():
            return _wrap(None,
                errors={'detalle': ['No hay aplicaciones completadas en este ciclo.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        calculadas = actualizadas = 0
        for aplicacion in aplicaciones:
            datos = calcular_resultado(aplicacion)

            resultado, created = ResultadoAplicacion.objects.update_or_create(
                aplicacion=aplicacion,
                defaults={
                    'puntaje_total': datos['puntaje_total'],
                    'puntaje_max':   datos['puntaje_max'],
                    'categoria':     datos['categoria'],
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

            if created:
                calculadas += 1
            else:
                actualizadas += 1

        return _wrap(None, meta={
            'ciclo_id':    ciclo.id,
            'ciclo_anio':  ciclo.anio,
            'calculadas':  calculadas,
            'actualizadas':actualizadas,
            'total':       calculadas + actualizadas,
        }, status_code=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """Resumen agregado de resultados para un ciclo."""
        ciclo_id = request.query_params.get('ciclo_id')
        if not ciclo_id:
            return _wrap(None,
                errors={'ciclo_id': ['Requerido.']},
                status_code=status.HTTP_400_BAD_REQUEST)

        tenant = request.user.tenant
        qs = self.get_queryset().filter(aplicacion__ciclo_id=ciclo_id)

        total = qs.count()
        dist  = {'bajo': 0, 'medio': 0, 'alto': 0, 'muy_alto': 0}
        for r in qs:
            dist[r.categoria] = dist.get(r.categoria, 0) + 1

        # Total completadas del ciclo (incluyendo las sin resultado calculado)
        total_completadas = Aplicacion.objects.filter(
            tenant=tenant, ciclo_id=ciclo_id, estado='completado').count()
        total_aplicaciones = Aplicacion.objects.filter(
            tenant=tenant, ciclo_id=ciclo_id).count()

        return _wrap({
            'total_resultados':   total,
            'total_completadas':  total_completadas,
            'total_aplicaciones': total_aplicaciones,
            'distribucion':       dist,
        })
