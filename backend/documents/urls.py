from django.urls import path
from .views import generar_informe, generar_reporte_psicologico

urlpatterns = [
    path('documentos/informe-nom035/', generar_informe, name='informe-nom035'),
    path('documentos/reporte-psicologico/', generar_reporte_psicologico, name='reporte-psicologico'),
]
