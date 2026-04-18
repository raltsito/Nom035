from datetime import date, timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notificacion
from .serializers import NotificacionSerializer


def _wrap(data, meta=None, errors=None, code=status.HTTP_200_OK):
    return Response({'data': data, 'meta': meta or {}, 'errors': errors}, status=code)


class NotificacionViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class   = NotificacionSerializer

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    def list(self, request, *args, **kwargs):
        qs     = self.get_queryset()[:50]
        no_leidas = self.get_queryset().filter(leida=False).count()
        return _wrap(
            NotificacionSerializer(qs, many=True).data,
            meta={'no_leidas': no_leidas},
        )

    def partial_update(self, request, pk=None):
        try:
            notif = self.get_queryset().get(pk=pk)
        except Notificacion.DoesNotExist:
            return _wrap(None, errors={'detail': 'No encontrada.'}, code=404)
        notif.leida = True
        notif.save(update_fields=['leida'])
        return _wrap(NotificacionSerializer(notif).data)

    def destroy(self, request, pk=None):
        try:
            notif = self.get_queryset().get(pk=pk)
        except Notificacion.DoesNotExist:
            return _wrap(None, errors={'detail': 'No encontrada.'}, code=404)
        notif.delete()
        return _wrap(None)

    @action(detail=False, methods=['post'], url_path='marcar_leidas')
    def marcar_leidas(self, request):
        updated = self.get_queryset().filter(leida=False).update(leida=True)
        return _wrap(None, meta={'actualizadas': updated})

    @action(detail=False, methods=['post'], url_path='generar')
    def generar(self, request):
        user   = request.user
        tenant = user.tenant
        if not tenant:
            return _wrap(None, meta={'creadas': 0})

        hoy     = date.today()
        creadas = 0

        # Acciones vencidas
        try:
            from m02_action_plan.models import AccionMedida
            acciones_vencidas = AccionMedida.objects.filter(
                tenant=tenant,
                estado__in=('pendiente', 'en_progreso'),
                fecha_limite__lt=hoy,
            )
            for accion in acciones_vencidas:
                ref = f'accion_{accion.id}'
                _, created = Notificacion.objects.get_or_create(
                    usuario=user, tipo='accion_vencida', referencia=ref,
                    defaults={
                        'titulo': 'Accion vencida en Plan de Accion',
                        'mensaje': f'"{accion.descripcion[:80]}" vencio el {accion.fecha_limite}.',
                        'url_destino': '/plan-accion',
                    },
                )
                if created:
                    creadas += 1

            # Acciones por vencer (7 dias)
            limite_prox = hoy + timedelta(days=7)
            acciones_prox = AccionMedida.objects.filter(
                tenant=tenant,
                estado__in=('pendiente', 'en_progreso'),
                fecha_limite__gte=hoy,
                fecha_limite__lte=limite_prox,
            )
            for accion in acciones_prox:
                ref = f'prox_accion_{accion.id}'
                _, created = Notificacion.objects.get_or_create(
                    usuario=user, tipo='accion_por_vencer', referencia=ref,
                    defaults={
                        'titulo': 'Accion proxima a vencer',
                        'mensaje': f'"{accion.descripcion[:80]}" vence el {accion.fecha_limite}.',
                        'url_destino': '/plan-accion',
                    },
                )
                if created:
                    creadas += 1
        except Exception:
            pass

        # Ciclos proximos a cerrar (30 dias)
        try:
            from m00_onboarding.models import CicloNOM
            limite_ciclo = hoy + timedelta(days=30)
            ciclos_prox  = CicloNOM.objects.filter(
                tenant=tenant,
                activo=True,
                fecha_fin__gte=hoy,
                fecha_fin__lte=limite_ciclo,
            )
            for ciclo in ciclos_prox:
                ref = f'ciclo_{ciclo.id}'
                _, created = Notificacion.objects.get_or_create(
                    usuario=user, tipo='ciclo_por_cerrar', referencia=ref,
                    defaults={
                        'titulo': f'Ciclo {ciclo.anio} proximo a cerrar',
                        'mensaje': f'El ciclo NOM-035 {ciclo.anio} cierra el {ciclo.fecha_fin}.',
                        'url_destino': '/dashboard',
                    },
                )
                if created:
                    creadas += 1
        except Exception:
            pass

        no_leidas = self.get_queryset().filter(leida=False).count()
        qs        = self.get_queryset()[:50]
        return _wrap(
            NotificacionSerializer(qs, many=True).data,
            meta={'creadas': creadas, 'no_leidas': no_leidas},
        )
