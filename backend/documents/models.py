from django.conf import settings
from django.db import models

from core.models import TenantAwareModel


class ReportePsicologico(TenantAwareModel):
    """Workflow borrador/aprobado del reporte psicológico NOM-035 por ciclo.

    Una vez aprobado, contenido_html_final queda congelado: el PDF que se
    entrega a partir de ese momento siempre se sirve desde ese snapshot,
    nunca recalculado contra datos que pudieron cambiar después.
    """

    ESTADO_BORRADOR = 'borrador'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_CHOICES = [
        (ESTADO_BORRADOR, 'Borrador'),
        (ESTADO_APROBADO, 'Aprobado'),
    ]

    ciclo = models.OneToOneField(
        'm00_onboarding.CicloNOM',
        on_delete=models.CASCADE,
        related_name='reporte_psicologico',
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_BORRADOR)
    anonimo = models.BooleanField(default=False)

    generado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_psico_generados',
    )
    generado_en = models.DateTimeField(null=True, blank=True)

    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_psico_revisados',
    )
    nombre_revisor = models.CharField(max_length=200, blank=True, default='')
    cedula_revisor = models.CharField(max_length=30, blank=True, default='')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    contenido_html_final = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Reporte psicológico'
        verbose_name_plural = 'Reportes psicológicos'
        ordering = ['-ciclo__anio']

    def __str__(self):
        return f'Reporte psicológico {self.tenant} — {self.ciclo} ({self.estado})'

    @property
    def is_aprobado(self):
        return self.estado == self.ESTADO_APROBADO
