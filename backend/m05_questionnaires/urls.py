from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CuestionarioViewSet, AplicacionViewSet, aplicacion_publica, responder_aplicacion

router = DefaultRouter()
router.register('cuestionarios', CuestionarioViewSet, basename='cuestionario')
router.register('aplicaciones',  AplicacionViewSet,   basename='aplicacion')

urlpatterns = router.urls + [
    path('publica/<uuid:token>/',          aplicacion_publica,   name='aplicacion-publica'),
    path('publica/<uuid:token>/responder/', responder_aplicacion, name='responder-aplicacion'),
]
