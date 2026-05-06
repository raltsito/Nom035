from django.db import models
from core.models import TenantAwareModel


class Trabajador(TenantAwareModel):
    TIPO_CHOICES = [
        ('planta',        'Planta'),
        ('eventual',      'Eventual'),
        ('subcontratado', 'Subcontratado'),
    ]

    nombre            = models.CharField(max_length=100, verbose_name='Nombre(s)')
    apellido_paterno  = models.CharField(max_length=100, verbose_name='Apellido paterno')
    apellido_materno  = models.CharField(max_length=100, blank=True, verbose_name='Apellido materno')
    num_empleado      = models.CharField(max_length=30, blank=True, verbose_name='No. de empleado')
    email             = models.EmailField(verbose_name='Correo electronico')
    puesto            = models.CharField(max_length=200, verbose_name='Puesto / cargo')
    area              = models.CharField(max_length=200, verbose_name='Area / departamento')
    tipo_contratacion = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='planta',
        verbose_name='Tipo de contratacion',
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name        = 'Trabajador'
        verbose_name_plural = 'Trabajadores'
        ordering            = ['apellido_paterno', 'apellido_materno', 'nombre']

    def __str__(self):
        return self.nombre_completo

    @property
    def nombre_completo(self):
        parts = [self.nombre, self.apellido_paterno]
        if self.apellido_materno:
            parts.append(self.apellido_materno)
        return ' '.join(parts)


class CicloNOM(TenantAwareModel):
    ESTADO_CHOICES = [
        ('iniciado',    'Iniciado'),
        ('en_progreso', 'En progreso'),
        ('completado',  'Completado'),
        ('cerrado',     'Cerrado'),
    ]

    anio         = models.PositiveIntegerField(verbose_name='Año')
    estado       = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='iniciado')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_cierre = models.DateField(null=True, blank=True, verbose_name='Fecha de cierre')
    notas        = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name        = 'Ciclo NOM-035'
        verbose_name_plural = 'Ciclos NOM-035'
        unique_together     = ('tenant', 'anio')
        ordering            = ['-anio']

    def __str__(self):
        return f'Ciclo {self.anio} — {self.tenant}'
