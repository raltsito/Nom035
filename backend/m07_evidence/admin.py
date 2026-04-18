from django.contrib import admin
from .models import EvidenciaDocumento


@admin.register(EvidenciaDocumento)
class EvidenciaDocumentoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'modulo', 'tipo_mime', 'tamanio', 'subido_por', 'tenant', 'ciclo', 'creado_en')
    list_filter   = ('modulo', 'ciclo', 'tenant')
    search_fields = ('nombre', 'descripcion')
    ordering      = ('-creado_en',)
