from django.db import models
from django.conf import settings


class Tenant(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre del centro de trabajo')
    razon_social = models.CharField(
        max_length=300, blank=True, verbose_name='Razon social',
        help_text='Razon social para informes. Si se deja vacia se usa el nombre del centro.')
    rfc = models.CharField(max_length=13, unique=True, verbose_name='RFC')
    giro = models.CharField(max_length=200, verbose_name='Giro o actividad')
    num_trabajadores = models.PositiveIntegerField(verbose_name='Numero de trabajadores')
    consultor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='tenants_asignados',
        limit_choices_to={'rol': 'super_admin'},
        verbose_name='Consultor asignado',
    )
    activo            = models.BooleanField(default=True, verbose_name='Activo')
    etiquetas_cortas  = models.BooleanField(default=False, verbose_name='Usar etiquetas cortas de tipo personal')
    logo_url          = models.URLField(blank=True, verbose_name='URL del logo')
    sitio_web         = models.URLField(blank=True, verbose_name='Sitio web')
    telefono_contacto = models.CharField(max_length=30, blank=True, verbose_name='Telefono de contacto')
    direccion         = models.CharField(max_length=400, blank=True, verbose_name='Direccion')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.rfc})'

    @property
    def guias_aplicables(self):
        n = self.num_trabajadores
        if n <= 15:
            return ['I']
        elif n <= 50:
            return ['I', 'III']
        return ['I', 'III', 'V']

    @property
    def categoria_tamano(self):
        n = self.num_trabajadores
        if n <= 15:
            return 'micro'
        elif n <= 50:
            return 'pequena'
        return 'mediana_grande'
