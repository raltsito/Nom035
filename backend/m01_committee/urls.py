from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComiteViewSet, MiembroViewSet, CapacitacionViewSet

router = DefaultRouter()
router.register('comite',          ComiteViewSet,    basename='comite')
router.register('miembros-comite', MiembroViewSet,   basename='miembros-comite')
router.register('dc3',             CapacitacionViewSet, basename='dc3')

urlpatterns = [
    path('', include(router.urls)),
]
