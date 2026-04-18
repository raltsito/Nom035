from django.db import models
from core.models import TenantAwareModel


TIPO_CHOICES = [
    ('preventiva', 'Preventiva'),
    ('correctiva', 'Correctiva'),
    ('mejora',     'Mejora continua'),
]

PRIORIDAD_CHOICES = [
    ('alta',  'Alta'),
    ('media', 'Media'),
    ('baja',  'Baja'),
]

ESTADO_CHOICES = [
    ('pendiente',   'Pendiente'),
    ('en_progreso', 'En progreso'),
    ('completado',  'Completado'),
    ('cancelado',   'Cancelado'),
]


class PlanAccion(TenantAwareModel):
    ciclo       = models.ForeignKey(
        'm00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='planes_accion'
    )
    descripcion = models.TextField(blank=True)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'ciclo')
        ordering        = ['-ciclo__anio']

    def __str__(self):
        return f'Plan de Accion {self.tenant} — {self.ciclo}'


class AccionMedida(TenantAwareModel):
    plan             = models.ForeignKey(PlanAccion, on_delete=models.CASCADE, related_name='acciones')
    descripcion      = models.TextField()
    tipo             = models.CharField(max_length=20, choices=TIPO_CHOICES, default='preventiva')
    factor_riesgo    = models.CharField(max_length=300, blank=True)
    responsable      = models.CharField(max_length=200)
    fecha_limite     = models.DateField()
    prioridad        = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    estado           = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    avance_notas     = models.TextField(blank=True)
    fecha_completado = models.DateField(null=True, blank=True)
    creado_en        = models.DateTimeField(auto_now_add=True)
    actualizado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fecha_limite', 'prioridad']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.descripcion[:60]}'
