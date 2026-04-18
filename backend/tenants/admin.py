from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rfc', 'num_trabajadores', 'guias_aplicables', 'consultor', 'activo')
    list_filter = ('activo', 'consultor')
    search_fields = ('nombre', 'rfc')
    readonly_fields = ('creado_en', 'actualizado_en', 'guias_aplicables', 'categoria_tamano')
