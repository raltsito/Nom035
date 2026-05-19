from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    SUPER_ADMIN = 'super_admin'
    TENANT_ADMIN = 'tenant_admin'
    EMPLEADO = 'empleado'
    AUDITOR = 'auditor'

    ROL_CHOICES = [
        (SUPER_ADMIN, 'Super Administrador'),
        (TENANT_ADMIN, 'Administrador de Empresa'),
        (EMPLEADO, 'Empleado'),
        (AUDITOR, 'Auditor'),
    ]

    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=EMPLEADO)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    @property
    def is_super_admin(self):
        return self.rol == self.SUPER_ADMIN

    @property
    def is_tenant_admin(self):
        return self.rol == self.TENANT_ADMIN

    @property
    def nombre_completo(self):
        return self.get_full_name() or self.email
