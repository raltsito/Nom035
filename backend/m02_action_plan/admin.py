from django.contrib import admin
from .models import PlanAccion, AccionMedida


class AccionInline(admin.TabularInline):
    model  = AccionMedida
    extra  = 0
    fields = ('descripcion', 'tipo', 'responsable', 'fecha_limite', 'prioridad', 'estado')


@admin.register(PlanAccion)
class PlanAccionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'ciclo', 'creado_en')
    list_filter  = ('tenant',)
    inlines      = (AccionInline,)


@admin.register(AccionMedida)
class AccionMedidaAdmin(admin.ModelAdmin):
    list_display  = ('descripcion', 'tipo', 'responsable', 'fecha_limite', 'prioridad', 'estado')
    list_filter   = ('tipo', 'prioridad', 'estado')
    search_fields = ('descripcion', 'responsable')
