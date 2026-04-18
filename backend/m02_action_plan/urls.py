from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanAccionViewSet, AccionMedidaViewSet

router = DefaultRouter()
router.register('plan-accion',  PlanAccionViewSet,  basename='plan-accion')
router.register('acciones',     AccionMedidaViewSet, basename='acciones')

urlpatterns = [
    path('', include(router.urls)),
]
