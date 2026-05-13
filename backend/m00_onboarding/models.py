from django.db import models
from core.models import TenantAwareModel


class Trabajador(TenantAwareModel):
    TIPO_CHOICES = [
        ('planta',        'Planta'),
        ('eventual',      'Eventual'),
        ('subcontratado', 'Subcontratado'),
    ]
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    ESTADO_CIVIL_CHOICES = [
        ('soltero',     'Soltero'),
        ('casado',      'Casado'),
        ('union_libre', 'Union libre'),
        ('divorciado',  'Divorciado'),
        ('viudo',       'Viudo'),
        ('otro',        'Otro'),
    ]
    NIVEL_ESTUDIOS_CHOICES = [
        ('primaria',      'Primaria'),
        ('secundaria',    'Secundaria'),
        ('bachillerato',  'Bachillerato / Preparatoria'),
        ('tecnico',       'Tecnico'),
        ('licenciatura',  'Licenciatura'),
        ('ingenieria',    'Ingenieria'),
        ('posgrado',      'Posgrado'),
        ('otro',          'Otro'),
    ]
    TIPO_PERSONAL_CHOICES = [
        ('sindicalizado', 'Sindicalizado / Directo'),
        ('confianza',     'Confianza / Indirecto'),
        ('salary',        'Salary / Administrativo'),
        ('otro',          'Otro'),
    ]
    TIPO_JORNADA_CHOICES = [
        ('diurno',   'Diurno'),
        ('mixto',    'Mixto'),
        ('nocturno', 'Nocturno'),
    ]

    nombre            = models.CharField(max_length=100, verbose_name='Nombre(s)')
    apellido_paterno  = models.CharField(max_length=100, verbose_name='Apellido paterno')
    apellido_materno  = models.CharField(max_length=100, blank=True, verbose_name='Apellido materno')
    num_empleado      = models.CharField(max_length=30, blank=True, verbose_name='No. de empleado')
    email             = models.EmailField(blank=True, verbose_name='Correo electronico')
    puesto            = models.CharField(max_length=200, blank=True, verbose_name='Puesto / cargo')
    area              = models.CharField(max_length=200, blank=True, verbose_name='Area / departamento')
    tipo_contratacion = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='planta',
        verbose_name='Tipo de contratacion',
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    # Campos Guia V
    sexo             = models.CharField(max_length=1,  choices=SEXO_CHOICES,          blank=True, verbose_name='Sexo')
    edad             = models.PositiveSmallIntegerField(null=True, blank=True,                     verbose_name='Edad')
    estado_civil     = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES,   blank=True, verbose_name='Estado civil')
    nivel_estudios   = models.CharField(max_length=20, choices=NIVEL_ESTUDIOS_CHOICES, blank=True, verbose_name='Nivel de estudios')
    tipo_personal    = models.CharField(max_length=20, choices=TIPO_PERSONAL_CHOICES,  blank=True, verbose_name='Tipo de personal')
    tipo_jornada     = models.CharField(max_length=10, choices=TIPO_JORNADA_CHOICES,   blank=True, verbose_name='Tipo de jornada')
    rotacion_turnos  = models.BooleanField(null=True, blank=True,                                  verbose_name='Realiza rotacion de turnos')
    experiencia_anios      = models.FloatField(null=True, blank=True, verbose_name='Experiencia en anos')
    tiempo_puesto_actual   = models.FloatField(null=True, blank=True, verbose_name='Tiempo en puesto actual')

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
