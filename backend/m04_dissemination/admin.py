from django.contrib import admin
from .models import ActividadDifusion


@admin.register(ActividadDifusion)
class ActividadDifusionAdmin(admin.ModelAdmin):
    list_display  = ('titulo', 'tipo', 'fecha', 'num_participantes', 'responsable', 'tenant', 'ciclo')
    list_filter   = ('tipo', 'ciclo', 'tenant')
    search_fields = ('titulo', 'responsable')
    ordering      = ('-fecha',)
