from django.db import models
from django.conf import settings


TIPO_CHOICES = [
    ('accion_vencida',    'Accion vencida'),
    ('accion_por_vencer', 'Accion por vencer'),
    ('ciclo_por_cerrar',  'Ciclo proximo a cerrar'),
    ('info',              'Informacion'),
]


class Notificacion(models.Model):
    usuario     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones'
    )
    tipo        = models.CharField(max_length=30, choices=TIPO_CHOICES, default='info')
    titulo      = models.CharField(max_length=200)
    mensaje     = models.TextField(blank=True)
    leida       = models.BooleanField(default=False)
    url_destino = models.CharField(max_length=200, blank=True)
    referencia  = models.CharField(max_length=100, blank=True)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ['-creado_en']
        unique_together = ('usuario', 'tipo', 'referencia')

    def __str__(self):
        return f'[{self.tipo}] {self.titulo} → {self.usuario}'
