from django.db import models
from core.models import TenantAwareModel


TIPO_CHOICES = [
    ('comite',       'Reunion de Comite'),
    ('capacitacion', 'Sesion de Capacitacion'),
    ('seguimiento',  'Reunion de Seguimiento'),
    ('informativa',  'Sesion Informativa'),
    ('otra',         'Otra'),
]


class Reunion(TenantAwareModel):
    ciclo          = models.ForeignKey(
        'm00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='reuniones'
    )
    tipo           = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otra')
    titulo         = models.CharField(max_length=300)
    fecha          = models.DateField()
    lugar          = models.CharField(max_length=200, blank=True)
    agenda         = models.TextField(blank=True)
    minuta         = models.TextField(blank=True)
    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.titulo} ({self.fecha})'


class Asistente(TenantAwareModel):
    reunion        = models.ForeignKey(
        Reunion, on_delete=models.CASCADE, related_name='asistentes'
    )
    nombre         = models.CharField(max_length=200)
    puesto         = models.CharField(max_length=200, blank=True)
    firma_recibida = models.BooleanField(default=False)
    creado_en      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} — {self.reunion}'
