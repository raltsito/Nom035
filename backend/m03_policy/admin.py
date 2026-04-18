from django.contrib import admin
from .models import PoliticaPrevension


@admin.register(PoliticaPrevension)
class PoliticaAdmin(admin.ModelAdmin):
    list_display  = ('tenant', 'ciclo', 'estado', 'firmante_nombre', 'fecha_aprobacion')
    list_filter   = ('estado', 'tenant')
    search_fields = ('titulo', 'firmante_nombre')
