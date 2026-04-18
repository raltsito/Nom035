from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, MiEmpresaView

router = DefaultRouter()
router.register('', TenantViewSet, basename='tenant')

urlpatterns = [
    path('mi-empresa/', MiEmpresaView.as_view(), name='mi-empresa'),
    path('', include(router.urls)),
]
