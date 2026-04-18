from rest_framework import serializers
from .models import PoliticaPrevension


class PoliticaPrevencionSerializer(serializers.ModelSerializer):
    estado_label   = serializers.CharField(source='get_estado_display', read_only=True)
    ciclo_anio     = serializers.IntegerField(source='ciclo.anio', read_only=True)

    class Meta:
        model  = PoliticaPrevension
        fields = (
            'id', 'ciclo', 'ciclo_anio', 'titulo', 'contenido',
            'estado', 'estado_label',
            'firmante_nombre', 'firmante_puesto', 'fecha_aprobacion',
            'creado_en', 'actualizado_en',
        )
        read_only_fields = ('id', 'estado_label', 'ciclo_anio', 'creado_en', 'actualizado_en')
