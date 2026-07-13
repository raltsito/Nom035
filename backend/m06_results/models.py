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

    class Meta:
        verbose_name = 'Resultado'
        verbose_name_plural = 'Resultados'

    def __str__(self):
        return f'{self.aplicacion} — {self.categoria}'


class ResultadoDominio(models.Model):
    resultado   = models.ForeignKey(
        ResultadoAplicacion, on_delete=models.CASCADE, related_name='dominios')
    dominio     = models.ForeignKey(Dominio, on_delete=models.CASCADE)
    puntaje     = models.PositiveSmallIntegerField()
    puntaje_max = models.PositiveSmallIntegerField()
    categoria   = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    class Meta:
        ordering = ['dominio__orden']
        verbose_name = 'Resultado por dominio'

    def __str__(self):
        return f'{self.resultado} / {self.dominio.clave}'


class ResultadoDominioOficial(models.Model):
    """Resultado de Guía III reagrupado en los 10 dominios oficiales de la
    Tabla 6 (Guía de Referencia III). No es FK a `Dominio`: los dominios
    oficiales no son un subconjunto de los 14 bloques crudos del cuestionario
    (algunos bloques se dividen entre dos dominios oficiales, otros se
    funden en uno solo) — ver `m06_results.scoring._dominio_oficial`.
    `ResultadoDominio` (14 bloques crudos) se conserva sin cambios para la
    sección "Dimensiones" del informe DOCX y el detalle por trabajador."""
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

    def __str__(self):
        return f'{self.resultado} / {self.nombre}'
