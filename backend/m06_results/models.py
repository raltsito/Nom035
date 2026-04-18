from django.db import models
from m05_questionnaires.models import Aplicacion, Dominio

CATEGORIA_CHOICES = [
    ('bajo',     'Nulo / Bajo'),
    ('medio',    'Medio'),
    ('alto',     'Alto'),
    ('muy_alto', 'Muy alto'),
]


class ResultadoAplicacion(models.Model):
    aplicacion    = models.OneToOneField(
        Aplicacion, on_delete=models.CASCADE, related_name='resultado')
    puntaje_total = models.PositiveSmallIntegerField()
    puntaje_max   = models.PositiveSmallIntegerField()
    categoria     = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    calculado_en  = models.DateTimeField(auto_now=True)

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
