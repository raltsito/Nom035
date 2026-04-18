from django.db import models
from core.models import TenantAwareModel


TIPO_CHOICES = [
    ('presidente', 'Presidente'),
    ('secretario', 'Secretario'),
    ('vocal',      'Vocal'),
]


class ComiteNOM(TenantAwareModel):
    ciclo              = models.ForeignKey(
        'm00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='comites'
    )
    fecha_constitucion = models.DateField()
    numero_acta        = models.CharField(max_length=50, blank=True)
    observaciones      = models.TextField(blank=True)
    creado_en          = models.DateTimeField(auto_now_add=True)
    actualizado_en     = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tenant', 'ciclo')
        ordering        = ['-ciclo__anio']

    def __str__(self):
        return f'Comite {self.tenant} — {self.ciclo}'


class MiembroComite(TenantAwareModel):
    comite   = models.ForeignKey(ComiteNOM, on_delete=models.CASCADE, related_name='miembros')
    nombre   = models.CharField(max_length=200)
    puesto   = models.CharField(max_length=200)
    tipo     = models.CharField(max_length=20, choices=TIPO_CHOICES, default='vocal')
    email    = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo   = models.BooleanField(default=True)

    class Meta:
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_display()})'


class CapacitacionDC3(TenantAwareModel):
    miembro           = models.ForeignKey(
        MiembroComite, on_delete=models.CASCADE, related_name='capacitaciones'
    )
    tipo_capacitacion = models.CharField(max_length=300)
    fecha             = models.DateField()
    horas             = models.PositiveSmallIntegerField(default=8)
    instructor        = models.CharField(max_length=200, blank=True)
    numero_dc3        = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'DC3 {self.miembro} — {self.tipo_capacitacion}'
