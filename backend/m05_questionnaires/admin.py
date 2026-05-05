from django.contrib import admin
from .models import Cuestionario, Dominio, Pregunta, Aplicacion, RespuestaPregunta, GuiaLink


class DominioInline(admin.TabularInline):
    model = Dominio
    extra = 0

class PreguntaInline(admin.TabularInline):
    model = Pregunta
    extra = 0

@admin.register(Cuestionario)
class CuestionarioAdmin(admin.ModelAdmin):
    list_display = ('clave', 'nombre', 'tamano_min', 'tamano_max')
    inlines = [DominioInline]

@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):
    list_display = ('cuestionario', 'orden', 'clave', 'nombre')
    list_filter = ('cuestionario',)
    inlines = [PreguntaInline]

@admin.register(Aplicacion)
class AplicacionAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'cuestionario', 'ciclo', 'estado', 'fecha_completado', 'tenant')
    list_filter = ('estado', 'cuestionario', 'tenant')
    readonly_fields = ('token',)

@admin.register(RespuestaPregunta)
class RespuestaPreguntaAdmin(admin.ModelAdmin):
    list_display = ('aplicacion', 'pregunta', 'valor')
    list_filter = ('aplicacion__cuestionario',)

@admin.register(GuiaLink)
class GuiaLinkAdmin(admin.ModelAdmin):
    list_display = ('cuestionario', 'ciclo', 'activo', 'token', 'tenant')
    list_filter = ('activo', 'cuestionario', 'tenant')
    readonly_fields = ('token',)
