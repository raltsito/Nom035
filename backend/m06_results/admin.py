from django.contrib import admin
from .models import ResultadoAplicacion, ResultadoDominio, ResultadoDominioOficial


class ResultadoDominioInline(admin.TabularInline):
    model       = ResultadoDominio
    extra       = 0
    fields      = ('dominio', 'puntaje', 'puntaje_max', 'categoria')
    readonly_fields = ('dominio', 'puntaje', 'puntaje_max', 'categoria')
    can_delete  = False


class ResultadoDominioOficialInline(admin.TabularInline):
    model       = ResultadoDominioOficial
    extra       = 0
    fields      = ('clave', 'nombre', 'puntaje', 'puntaje_max', 'categoria')
    readonly_fields = ('clave', 'nombre', 'puntaje', 'puntaje_max', 'categoria')
    can_delete  = False


@admin.register(ResultadoAplicacion)
class ResultadoAplicacionAdmin(admin.ModelAdmin):
    list_display  = ('aplicacion', 'puntaje_total', 'puntaje_max', 'categoria', 'calculado_en')
    list_filter   = ('categoria', 'aplicacion__cuestionario')
    readonly_fields = ('calculado_en',)
    inlines       = [ResultadoDominioInline, ResultadoDominioOficialInline]
