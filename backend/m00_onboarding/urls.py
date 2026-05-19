from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TrabajadorViewSet, CicloNOMViewSet, resumen_muestra_view, sugeridos_muestra_view, exportar_muestra_excel

router = DefaultRouter()
router.register('trabajadores', TrabajadorViewSet, basename='trabajador')
router.register('ciclos', CicloNOMViewSet, basename='ciclo')

urlpatterns = [
    path('trabajadores/resumen-muestra/',    resumen_muestra_view,   name='trabajador-resumen-muestra'),
    path('trabajadores/sugeridos-muestra/',  sugeridos_muestra_view, name='trabajador-sugeridos-muestra'),
    path('trabajadores/exportar-muestra/',   exportar_muestra_excel, name='trabajador-exportar-muestra'),
] + router.urls
