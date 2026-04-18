from django.contrib import admin
from .models import Reunion, Asistente


@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display  = ('titulo', 'tipo', 'fecha', 'lugar', 'tenant', 'ciclo')
    list_filter   = ('tipo', 'ciclo', 'tenant')
    search_fields = ('titulo',)
    ordering      = ('-fecha',)


@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'puesto', 'firma_recibida', 'reunion')
    list_filter   = ('firma_recibida', 'reunion__tipo')
    search_fields = ('nombre',)
