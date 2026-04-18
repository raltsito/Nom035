from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActividadDifusionViewSet

router = DefaultRouter()
router.register('actividades-difusion', ActividadDifusionViewSet, basename='actividades-difusion')

urlpatterns = [
    path('', include(router.urls)),
]
