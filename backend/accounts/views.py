from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsSuperAdmin, IsTenantAdmin


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({'data': response.data, 'meta': {}, 'errors': None})
        return response


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'data': None, 'meta': {}, 'errors': None})
        except Exception:
            return Response(
                {'data': None, 'meta': {}, 'errors': {'detail': 'Token invalido.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'data': serializer.data, 'meta': {}, 'errors': None})

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data, 'meta': {}, 'errors': None})
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'data': None, 'meta': {}, 'errors': None})
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    Gestion de usuarios.
    - Super Admin: ve y gestiona todos los usuarios de sus tenants.
    - Tenant Admin: ve y gestiona solo los usuarios de su tenant.
    """
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('list', 'create', 'destroy'):
            return [IsTenantAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return User.objects.select_related('tenant').all()
        return User.objects.filter(tenant=user.tenant).select_related('tenant')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            if not user.is_super_admin:
                instance = serializer.save(tenant=user.tenant)
            else:
                instance = serializer.save()
            return Response(
                {'data': UserSerializer(instance).data, 'meta': {}, 'errors': None},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'meta': {'count': queryset.count()},
            'errors': None,
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'data': serializer.data, 'meta': {}, 'errors': None})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data, 'meta': {}, 'errors': None})
        return Response(
            {'data': None, 'meta': {}, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
