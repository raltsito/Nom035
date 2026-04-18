from collections import defaultdict

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsSuperAdmin, IsTenantAdmin
from .models import Tenant
from .serializers import TenantSerializer, TenantCreateSerializer, TenantUpdateSerializer, TenantBrandingSerializer


class TenantViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSuperAdmin,)
    serializer_class = TenantSerializer

    def get_queryset(self):
        return Tenant.objects.filter(consultor=self.request.user).order_by('nombre')

    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        if self.action in ('update', 'partial_update'):
            return TenantUpdateSerializer
        return TenantSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        q = request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(nombre__icontains=q) | qs.filter(rfc__icontains=q)
        serializer = TenantSerializer(qs, many=True)
        return Response({
            'data': serializer.data,
            'meta': {'count': qs.count()},
            'errors': None,
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TenantSerializer(instance)
        return Response({'data': serializer.data, 'meta': {}, 'errors': None})

    def create(self, request, *args, **kwargs):
        serializer = TenantCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                {'data': TenantSerializer(instance).data, 'meta': {}, 'errors': None},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):  # noqa: WPS473
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = TenantUpdateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': TenantSerializer(instance).data, 'meta': {}, 'errors': None})
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'data': None, 'meta': {}, 'errors': None}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-activo')
    def toggle_activo(self, request, pk=None):
        instance = self.get_object()
        instance.activo = not instance.activo
        instance.save(update_fields=['activo'])
        return Response({'data': TenantSerializer(instance).data, 'meta': {}, 'errors': None})

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        from m00_onboarding.models import Trabajador, CicloNOM
        from m05_questionnaires.models import Aplicacion
        from m06_results.models import ResultadoAplicacion

        instance = self.get_object()

        total_trabajadores = Trabajador.objects.filter(tenant=instance).count()
        total_ciclos       = CicloNOM.objects.filter(tenant=instance).count()
        aplicaciones       = Aplicacion.objects.filter(tenant=instance)
        total_aplicaciones = aplicaciones.count()
        total_completadas  = aplicaciones.filter(estado='completado').count()
        resultados         = ResultadoAplicacion.objects.filter(aplicacion__tenant=instance)
        total_resultados   = resultados.count()

        dist = defaultdict(int)
        for cat in resultados.values_list('categoria', flat=True):
            dist[cat] += 1

        return Response({
            'data': {
                'total_trabajadores': total_trabajadores,
                'total_ciclos':       total_ciclos,
                'total_aplicaciones': total_aplicaciones,
                'total_completadas':  total_completadas,
                'total_resultados':   total_resultados,
                'distribucion': {
                    'bajo':     dist['bajo'],
                    'medio':    dist['medio'],
                    'alto':     dist['alto'],
                    'muy_alto': dist['muy_alto'],
                },
            },
            'meta': {},
            'errors': None,
        })

    @action(detail=True, methods=['get', 'post'], url_path='usuarios')
    def usuarios(self, request, pk=None):
        from accounts.models import User
        from accounts.serializers import UserSerializer, UserCreateSerializer

        instance = self.get_object()

        if request.method == 'GET':
            users = User.objects.filter(tenant=instance).order_by('first_name', 'last_name')
            serializer = UserSerializer(users, many=True)
            return Response({
                'data': serializer.data,
                'meta': {'count': users.count()},
                'errors': None,
            })

        # POST — create a tenant_admin for this tenant
        data = {**request.data, 'tenant': instance.id, 'rol': 'tenant_admin'}
        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'data': UserSerializer(user).data, 'meta': {}, 'errors': None},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class MiEmpresaView(APIView):
    permission_classes = (IsTenantAdmin,)

    def get(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({'data': None, 'meta': {}, 'errors': {'detail': 'Sin empresa asignada.'}}, status=400)
        return Response({'data': TenantBrandingSerializer(tenant).data, 'meta': {}, 'errors': None})

    def patch(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({'data': None, 'meta': {}, 'errors': {'detail': 'Sin empresa asignada.'}}, status=400)
        serializer = TenantBrandingSerializer(tenant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': TenantBrandingSerializer(tenant).data, 'meta': {}, 'errors': None})
        return Response({'data': None, 'meta': {}, 'errors': serializer.errors}, status=400)
