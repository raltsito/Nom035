from django.urls import path

from .views import (
    descargar_informe_diagnostico,
    exportar_matriz_guia_i_excel,
    exportar_matriz_resultados_excel,
    exportar_respuestas_excel,
    reporte_psicologico_aprobar,
    reporte_psicologico_borrador,
    reporte_psicologico_descargar,
    reporte_psicologico_estado,
)

urlpatterns = [
    path('documentos/informe-diagnostico/', descargar_informe_diagnostico, name='informe-diagnostico'),
    path('documentos/respuestas-nom035/', exportar_respuestas_excel, name='respuestas-nom035'),
    path('documentos/matriz-resultados/', exportar_matriz_resultados_excel, name='matriz-resultados'),
    path('documentos/matriz-guia-i/', exportar_matriz_guia_i_excel, name='matriz-guia-i'),
    path('documentos/reporte-psicologico/', reporte_psicologico_descargar, name='reporte-psicologico'),
    path('documentos/reporte-psicologico/borrador/', reporte_psicologico_borrador, name='reporte-psicologico-borrador'),
    path('documentos/reporte-psicologico/aprobar/', reporte_psicologico_aprobar, name='reporte-psicologico-aprobar'),
    path('documentos/reporte-psicologico/estado/', reporte_psicologico_estado, name='reporte-psicologico-estado'),
]
