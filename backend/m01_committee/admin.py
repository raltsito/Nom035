from django.contrib import admin
from .models import ComiteNOM, MiembroComite, CapacitacionDC3


class MiembroInline(admin.TabularInline):
    model = MiembroComite
    extra = 0


class DC3Inline(admin.TabularInline):
    model = CapacitacionDC3
    extra = 0


@admin.register(ComiteNOM)
class ComiteAdmin(admin.ModelAdmin):
    list_display  = ('tenant', 'ciclo', 'fecha_constitucion', 'numero_acta')
    list_filter   = ('tenant',)
    inlines       = (MiembroInline,)


@admin.register(MiembroComite)
class MiembroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'puesto', 'comite', 'activo')
    list_filter  = ('tipo', 'activo')
    inlines      = (DC3Inline,)


@admin.register(CapacitacionDC3)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('miembro', 'tipo_capacitacion', 'fecha', 'horas', 'numero_dc3')
