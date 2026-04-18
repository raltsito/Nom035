from django.db import models
from core.models import TenantAwareModel


ESTADO_CHOICES = [
    ('borrador', 'Borrador'),
    ('vigente',  'Vigente'),
    ('archivada','Archivada'),
]


class PoliticaPrevension(TenantAwareModel):
    ciclo           = models.ForeignKey(
        'm00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='politicas'
    )
    titulo          = models.CharField(
        max_length=300,
        default='Política de Prevención de Factores de Riesgo Psicosocial',
    )
    contenido       = models.TextField()
    estado          = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    firmante_nombre = models.CharField(max_length=200, blank=True)
    firmante_puesto = models.CharField(max_length=200, blank=True)
    fecha_aprobacion = models.DateField(null=True, blank=True)
    creado_en       = models.DateTimeField(auto_now_add=True)
    actualizado_en  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tenant', 'ciclo')
        ordering        = ['-ciclo__anio']

    def __str__(self):
        return f'Politica {self.tenant} — {self.ciclo} ({self.estado})'
