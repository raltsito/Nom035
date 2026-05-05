from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CuestionarioViewSet, AplicacionViewSet, GuiaLinkViewSet,
    aplicacion_publica, responder_aplicacion,
    guia_link_publica, identificar_trabajador, confirmar_trabajador,
)

router = DefaultRouter()
router.register('cuestionarios', CuestionarioViewSet, basename='cuestionario')
router.register('aplicaciones',  AplicacionViewSet,   basename='aplicacion')
router.register('guia-links',    GuiaLinkViewSet,     basename='guia-link')

urlpatterns = router.urls + [
    path('publica/guia/<uuid:token>/',             guia_link_publica,      name='guia-link-publica'),
    path('publica/guia/<uuid:token>/identificar/', identificar_trabajador, name='identificar-trabajador'),
    path('publica/guia/<uuid:token>/confirmar/',   confirmar_trabajador,   name='confirmar-trabajador'),
    path('publica/<uuid:token>/',                  aplicacion_publica,     name='aplicacion-publica'),
    path('publica/<uuid:token>/responder/',        responder_aplicacion,   name='responder-aplicacion'),
]
