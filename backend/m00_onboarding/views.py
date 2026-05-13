from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from accounts.permissions import IsTenantAdmin
from .models import Trabajador, CicloNOM
from .serializers import (
    TrabajadorSerializer, TrabajadorCreateSerializer, TrabajadorUpdateSerializer,
    CicloNOMSerializer, CicloNOMCreateSerializer,
)
from .importador import importar_excel


class TrabajadorViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = TrabajadorSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            qs = Trabajador.objects.all()
            tenant_id = self.request.query_params.get('tenant_id')
            if tenant_id:
                qs = qs.filter(tenant_id=tenant_id)
        else:
            qs = Trabajador.objects.filter(tenant=user.tenant)
        return qs.order_by('apellido_paterno', 'apellido_materno', 'nombre')

    def get_serializer_class(self):
        if self.action == 'create':
            return TrabajadorCreateSerializer
        if self.action in ('update', 'partial_update'):
            return TrabajadorUpdateSerializer
        return TrabajadorSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        q = request.query_params.get('q', '').strip()
        if q:
            qs = (
                qs.filter(nombre__icontains=q) |
                qs.filter(apellido_paterno__icontains=q) |
                qs.filter(apellido_materno__icontains=q) |
                qs.filter(num_empleado__icontains=q) |
                qs.filter(email__icontains=q) |
                qs.filter(area__icontains=q) |
                qs.filter(puesto__icontains=q)
            ).distinct()

        solo_activos = request.query_params.get('activos')
        if solo_activos == '1':
            qs = qs.filter(activo=True)

        serializer = TrabajadorSerializer(qs, many=True)
        return Response({
            'data': serializer.data,
            'meta': {'count': qs.count()},
            'errors': None,
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'data': TrabajadorSerializer(instance).data, 'meta': {}, 'errors': None})

    def create(self, request, *args, **kwargs):
        serializer = TrabajadorCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                {'data': TrabajadorSerializer(instance).data, 'meta': {}, 'errors': None},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial  = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = TrabajadorUpdateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': TrabajadorSerializer(instance).data, 'meta': {}, 'errors': None})
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
        return Response({'data': TrabajadorSerializer(instance).data, 'meta': {}, 'errors': None})

    @action(
        detail=False,
        methods=['post'],
        url_path='importar-excel',
        parser_classes=[MultiPartParser],
    )
    def importar_excel(self, request):
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response(
                {'data': None, 'meta': {}, 'errors': {'archivo': ['Se requiere un archivo Excel.']}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = archivo.name.rsplit('.', 1)[-1].lower()
        if ext not in ('xlsx', 'xls'):
            return Response(
                {'data': None, 'meta': {}, 'errors': {'archivo': ['Solo se aceptan archivos .xlsx o .xls.']}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Super admin puede importar a cualquier tenant vía ?tenant_id=
        if request.user.is_super_admin:
            from django.apps import apps
            tenant_id = request.query_params.get('tenant_id') or request.data.get('tenant_id')
            if not tenant_id:
                return Response(
                    {'data': None, 'meta': {}, 'errors': {'tenant_id': ['Especifica el tenant.']}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Tenant = apps.get_model('accounts', 'Tenant')
            try:
                tenant = Tenant.objects.get(pk=tenant_id)
            except Tenant.DoesNotExist:
                return Response(
                    {'data': None, 'meta': {}, 'errors': {'tenant_id': ['Tenant no encontrado.']}},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            tenant = request.user.tenant

        try:
            resultado = importar_excel(archivo, tenant)
        except Exception as exc:
            return Response(
                {'data': None, 'meta': {}, 'errors': {'archivo': [f'Error al procesar el archivo: {exc}']}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'data': resultado,
            'meta': {'tenant': str(tenant)},
            'errors': None,
        }, status=status.HTTP_200_OK)


class CicloNOMViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTenantAdmin,)
    serializer_class   = CicloNOMSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return CicloNOM.objects.all()
        return CicloNOM.objects.filter(tenant=user.tenant)

    def get_serializer_class(self):
        if self.action == 'create':
            return CicloNOMCreateSerializer
        return CicloNOMSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = CicloNOMSerializer(qs, many=True)
        return Response({
            'data': serializer.data,
            'meta': {'count': qs.count()},
            'errors': None,
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'data': CicloNOMSerializer(instance).data, 'meta': {}, 'errors': None})

    def create(self, request, *args, **kwargs):
        serializer = CicloNOMCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                {'data': CicloNOMSerializer(instance).data, 'meta': {}, 'errors': None},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        partial  = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = CicloNOMSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': CicloNOMSerializer(instance).data, 'meta': {}, 'errors': None})
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'data': None, 'meta': {}, 'errors': None}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='avanzar-estado')
    def avanzar_estado(self, request, pk=None):
        instance = self.get_object()
        flujo = ['iniciado', 'en_progreso', 'completado', 'cerrado']
        idx   = flujo.index(instance.estado)
        if idx < len(flujo) - 1:
            instance.estado = flujo[idx + 1]
            instance.save(update_fields=['estado'])
        return Response({'data': CicloNOMSerializer(instance).data, 'meta': {}, 'errors': None})
