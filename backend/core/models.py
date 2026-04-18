from django.db import models
from core.managers import TenantManager


class TenantAwareModel(models.Model):
    """
    Modelo base para cualquier entidad que pertenece a un tenant especifico.
    Todos los modulos de negocio deben heredar de este modelo.
    """

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='+',
        db_index=True,
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
