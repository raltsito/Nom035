from django.db import models
from m05_questionnaires.models import Aplicacion, Dominio

CATEGORIA_CHOICES = [
    ('nulo',                'Nulo / despreciable'),
    ('bajo',                'Bajo'),
    ('medio',               'Medio'),
    ('alto',                'Alto'),
    ('muy_alto',            'Muy alto'),
    # Exclusivo Guía I
    ('requiere_atencion',   'Requiere atención clínica'),
    ('sin_indicadores',     'Sin indicadores'),
    # Cuestionario inválido/incompleto: NO se clasifica (ver scoring.py)
    ('sin_calificar',       'Sin calificar (requiere revisión)'),
]

ESTATUS_VALIDACION_CHOICES = [
    ('valido',            'Válido'),
    ('requiere_revision', 'Requiere revisión'),
]


class ResultadoAplicacion(models.Model):
    aplicacion        = models.OneToOneField(
        Aplicacion, on_delete=models.CASCADE, related_name='resultado')
    puntaje_total     = models.PositiveSmallIntegerField()
    puntaje_max       = models.PositiveSmallIntegerField()
    categoria         = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    requiere_atencion = models.BooleanField(
        null=True, blank=True,
        help_text='Solo Guía I. True = trabajador requiere evaluación clínica.')
    calculado_en      = models.DateTimeField(auto_now=True)

    # --- Trazabilidad / auditoría (auditoría metodológica 2026-07) ---
    estatus_validacion = models.CharField(
        max_length=20, choices=ESTATUS_VALIDACION_CHOICES, default='valido',
        help_text='Un cuestionario incompleto o inconsistente no se clasifica.')
    version_motor      = models.CharField(
        max_length=20, blank=True, default='',
        help_text='Versión de m06_results.scoring con la que se calculó.')
    hash_respuestas    = models.CharField(
        max_length=64, blank=True, default='',
        help_text='SHA-256 de las respuestas al momento del cálculo (reproducibilidad).')
    detalle            = models.JSONField(
        default=dict, blank=True,
        help_text='Validación estructurada y desgloses (secciones ATS, filtros, advertencias).')

    class Meta:
        verbose_name = 'Resultado'
        verbose_name_plural = 'Resultados'

    def __str__(self):
        return f'{self.aplicacion} — {self.categoria}'


class ResultadoDominio(models.Model):
    """Bloques internos de captura D1-D14 (Guía III) o secciones I-IV
    (Guía I). Para Guía III su `categoria` es un semáforo porcentual
    REFERENCIAL, no un nivel oficial de la NOM-035 (los niveles oficiales
    viven en ResultadoDominioOficial / ResultadoCategoria)."""
    resultado   = models.ForeignKey(
        ResultadoAplicacion, on_delete=models.CASCADE, related_name='dominios')
    dominio     = models.ForeignKey(Dominio, on_delete=models.CASCADE)
    puntaje     = models.PositiveSmallIntegerField()
    puntaje_max = models.PositiveSmallIntegerField()
    categoria   = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    class Meta:
        ordering = ['dominio__orden']
        verbose_name = 'Resultado por bloque de captura'
        constraints = [
            models.UniqueConstraint(
                fields=['resultado', 'dominio'], name='uniq_resultado_bloque'),
        ]

    def __str__(self):
        return f'{self.resultado} / {self.dominio.clave}'


class ResultadoDominioOficial(models.Model):
    """Resultado de Guía III en los 10 dominios oficiales de la Tabla 6.
    `categoria` sí es el nivel oficial (cortes de suma de la GR.III)."""
    resultado   = models.ForeignKey(
        ResultadoAplicacion, on_delete=models.CASCADE, related_name='dominios_oficiales')
    clave       = models.CharField(max_length=10)
    nombre      = models.CharField(max_length=200)
    orden       = models.PositiveSmallIntegerField()
    puntaje     = models.PositiveSmallIntegerField()
    puntaje_max = models.PositiveSmallIntegerField()
    categoria   = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Resultado por dominio oficial'
        verbose_name_plural = 'Resultados por dominio oficial'
        constraints = [
            models.UniqueConstraint(
                fields=['resultado', 'clave'], name='uniq_resultado_dominio_oficial'),
        ]

    def __str__(self):
        return f'{self.resultado} / {self.nombre}'


class ResultadoCategoria(models.Model):
    """Las 5 categorías oficiales de la Tabla 6 (Guía III), clasificadas con
    los cortes oficiales de Ccat por cuestionario individual."""
    resultado   = models.ForeignKey(
        ResultadoAplicacion, on_delete=models.CASCADE, related_name='categorias')
    nombre      = models.CharField(max_length=200)
    orden       = models.PositiveSmallIntegerField()
    puntaje     = models.PositiveSmallIntegerField()
    puntaje_max = models.PositiveSmallIntegerField()
    categoria   = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Resultado por categoría oficial'
        verbose_name_plural = 'Resultados por categoría oficial'
        constraints = [
            models.UniqueConstraint(
                fields=['resultado', 'orden'], name='uniq_resultado_categoria'),
        ]

    def __str__(self):
        return f'{self.resultado} / {self.nombre}'


class ResultadoDimension(models.Model):
    """Las 25 dimensiones de la Tabla 6 (Guía III). La NOM-035 NO define
    puntos de corte por dimensión: este registro es SOLO descriptivo (suma,
    máximo aplicable y % del máximo), sin nivel de riesgo."""
    resultado       = models.ForeignKey(
        ResultadoAplicacion, on_delete=models.CASCADE, related_name='dimensiones')
    nombre          = models.CharField(max_length=200)
    dominio_oficial = models.CharField(max_length=200)
    orden           = models.PositiveSmallIntegerField()
    puntaje         = models.PositiveSmallIntegerField()
    puntaje_max     = models.PositiveSmallIntegerField()
    pct             = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        help_text='Porcentaje del máximo posible aplicable. Indicador descriptivo, no normativo.')

    class Meta:
        ordering = ['orden']
        verbose_name = 'Resultado por dimensión (descriptivo)'
        verbose_name_plural = 'Resultados por dimensión (descriptivos)'
        constraints = [
            models.UniqueConstraint(
                fields=['resultado', 'orden'], name='uniq_resultado_dimension'),
        ]

    def __str__(self):
        return f'{self.resultado} / {self.nombre}'
