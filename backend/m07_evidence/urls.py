from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EvidenciaViewSet

router = DefaultRouter()
router.register('evidencias', EvidenciaViewSet, basename='evidencias')

urlpatterns = [
    path('', include(router.urls)),
]
