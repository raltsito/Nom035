from django.contrib import admin
from .models import Trabajador, CicloNOM


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display  = ('nombre_completo', 'num_empleado', 'email', 'puesto', 'area', 'tipo_contratacion', 'activo', 'tenant')
    list_filter   = ('activo', 'tipo_contratacion', 'tenant')
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'num_empleado', 'email')


@admin.register(CicloNOM)
class CicloNOMAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'anio', 'estado', 'fecha_inicio', 'fecha_cierre')
    list_filter  = ('estado', 'anio', 'tenant')
