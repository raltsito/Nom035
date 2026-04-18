import threading
from django.db import models

_thread_locals = threading.local()


def set_current_tenant(tenant):
    _thread_locals.tenant = tenant


def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)


class TenantManager(models.Manager):
    """
    Filtra automaticamente por el tenant activo en el hilo actual.
    El Super Admin no tiene tenant en thread_locals, por lo que ve todos los registros.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is not None:
            return qs.filter(tenant=tenant)
        return qs
