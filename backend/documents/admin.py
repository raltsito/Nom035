from django.contrib import admin

from .models import ReportePsicologico

# Registro de modelos del modulo documents


@admin.register(ReportePsicologico)
class ReportePsicologicoAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'ciclo', 'estado', 'revisor', 'fecha_aprobacion')
    list_filter = ('estado', 'tenant')
    readonly_fields = (
        'tenant', 'ciclo', 'generado_por', 'generado_en',
        'revisor', 'nombre_revisor', 'cedula_revisor', 'fecha_aprobacion',
        'contenido_html_final', 'creado_en', 'actualizado_en',
    )
