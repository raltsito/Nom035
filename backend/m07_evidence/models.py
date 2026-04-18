from django.db import models
from core.models import TenantAwareModel


MODULO_CHOICES = [
    ('comite',     'Comite NOM-035'),
    ('plan',       'Plan de Accion'),
    ('politica',   'Politica de Prevencion'),
    ('difusion',   'Difusion'),
    ('aplicacion', 'Aplicacion de Cuestionarios'),
    ('otro',       'Otro'),
]


class EvidenciaDocumento(TenantAwareModel):
    ciclo       = models.ForeignKey(
        'm00_onboarding.CicloNOM', on_delete=models.CASCADE, related_name='evidencias'
    )
    modulo      = models.CharField(max_length=20, choices=MODULO_CHOICES, default='otro')
    nombre      = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    archivo     = models.FileField(upload_to='evidencias/%Y/%m/')
    tamanio     = models.PositiveIntegerField(default=0)
    tipo_mime   = models.CharField(max_length=120, blank=True)
    subido_por  = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='evidencias_subidas'
    )
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.nombre} ({self.get_modulo_display()})'
