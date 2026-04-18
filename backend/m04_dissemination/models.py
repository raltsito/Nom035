from django.db import models
from core.models import TenantAwareModel


TIPO_CHOICES = [
    ('platica',       'Platica / Capacitacion'),
    ('correo',        'Correo electronico'),
    ('cartel',        'Cartel / Material impreso'),
    ('reunion',       'Reunion de trabajo'),
    ('intranet',      'Intranet / Portal interno'),
    ('otro',          'Otro'),
]


class ActividadDifusion(TenantAwareModel):
    ciclo            = models.ForeignKey(
        'm00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='actividades_difusion'
    )
    tipo             = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo           = models.CharField(max_length=300)
    descripcion      = models.TextField(blank=True)
    fecha            = models.DateField()
    num_participantes = models.PositiveSmallIntegerField(default=0)
    responsable      = models.CharField(max_length=200, blank=True)
    creado_en        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.titulo} ({self.fecha})'
