import uuid
from django.db import models
from django.utils import timezone
from core.models import TenantAwareModel


class GuiaLink(TenantAwareModel):
    ciclo        = models.ForeignKey('m00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='guia_links')
    cuestionario = models.ForeignKey('Cuestionario', on_delete=models.PROTECT, related_name='guia_links')
    token        = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    activo       = models.BooleanField(default=True)

    class Meta:
        unique_together = ('ciclo', 'cuestionario')
        verbose_name        = 'Link de Guia'
        verbose_name_plural = 'Links de Guia'

    def __str__(self):
        return f'Guia {self.cuestionario.clave} — {self.ciclo}'


class Cuestionario(models.Model):
    clave       = models.CharField(max_length=5, unique=True)
    nombre      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tamano_min  = models.PositiveIntegerField()
    tamano_max  = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['tamano_min']
        verbose_name = 'Cuestionario'
        verbose_name_plural = 'Cuestionarios'

    def __str__(self):
        return f'Guia {self.clave} — {self.nombre}'


class Dominio(models.Model):
    cuestionario = models.ForeignKey(Cuestionario, on_delete=models.CASCADE, related_name='dominios')
    orden        = models.PositiveSmallIntegerField()
    clave        = models.CharField(max_length=10)
    nombre       = models.CharField(max_length=200)

    class Meta:
        ordering = ['orden']
        unique_together = ('cuestionario', 'orden')
        verbose_name = 'Dominio'

    def __str__(self):
        return f'{self.cuestionario.clave} – {self.nombre}'


class Pregunta(models.Model):
    TIPO_RESPUESTA_CHOICES = [
        ('frecuencia', 'Frecuencia'),
        ('si_no', 'Si/No'),
        ('texto', 'Texto'),
        ('opcion', 'Opcion'),
    ]

    dominio = models.ForeignKey(Dominio, on_delete=models.CASCADE, related_name='preguntas')
    orden   = models.PositiveSmallIntegerField()
    texto   = models.TextField()
    inversa = models.BooleanField(default=False)
    tipo_respuesta = models.CharField(max_length=20, choices=TIPO_RESPUESTA_CHOICES, default='frecuencia')
    opciones = models.JSONField(default=list, blank=True)
    condicion_pregunta = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preguntas_condicionadas',
    )
    condicion_preguntas = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='preguntas_condicionadas_multiples',
    )
    condicion_operador = models.CharField(
        max_length=10,
        choices=[('all', 'Todas'), ('any', 'Cualquiera')],
        default='all',
    )
    condicion_valor = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['orden']
        unique_together = ('dominio', 'orden')
        verbose_name = 'Pregunta'

    def __str__(self):
        return f'[{self.dominio.clave}] P{self.orden}'


class Aplicacion(TenantAwareModel):
    ESTADO_CHOICES = [
        ('pendiente',   'Pendiente'),
        ('en_progreso', 'En progreso'),
        ('completado',  'Completado'),
    ]

    ciclo        = models.ForeignKey('m00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='aplicaciones')
    cuestionario = models.ForeignKey(Cuestionario, on_delete=models.PROTECT, related_name='aplicaciones')
    trabajador   = models.ForeignKey('m00_onboarding.Trabajador', on_delete=models.CASCADE, related_name='aplicaciones')
    estado           = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    token            = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('ciclo', 'cuestionario', 'trabajador')
        ordering = ['trabajador__apellido_paterno', 'trabajador__nombre']
        verbose_name = 'Aplicacion'
        verbose_name_plural = 'Aplicaciones'

    def __str__(self):
        return f'{self.trabajador} — Guia {self.cuestionario.clave} ({self.estado})'

    def marcar_completado(self):
        self.estado          = 'completado'
        self.fecha_completado = timezone.now()
        self.save(update_fields=['estado', 'fecha_completado'])


class RespuestaPregunta(TenantAwareModel):
    VALOR_CHOICES = [
        (0, 'Nunca'),
        (1, 'Casi nunca'),
        (2, 'Algunas veces'),
        (3, 'Casi siempre'),
        (4, 'Siempre'),
    ]

    aplicacion = models.ForeignKey(Aplicacion, on_delete=models.CASCADE, related_name='respuestas')
    pregunta   = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    valor      = models.PositiveSmallIntegerField(choices=VALOR_CHOICES, null=True, blank=True)
    valor_texto = models.TextField(blank=True)

    class Meta:
        unique_together = ('aplicacion', 'pregunta')
        verbose_name = 'Respuesta'

    @property
    def valor_ponderado(self):
        return (4 - self.valor) if self.pregunta.inversa else self.valor
