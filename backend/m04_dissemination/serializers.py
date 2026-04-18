from rest_framework import serializers
from .models import ActividadDifusion


class ActividadDifusionSerializer(serializers.ModelSerializer):
    tipo_label  = serializers.CharField(source='get_tipo_display', read_only=True)
    ciclo_anio  = serializers.IntegerField(source='ciclo.anio', read_only=True)

    class Meta:
        model  = ActividadDifusion
        fields = (
            'id', 'ciclo', 'ciclo_anio', 'tipo', 'tipo_label',
            'titulo', 'descripcion', 'fecha', 'num_participantes',
            'responsable', 'creado_en',
        )
        read_only_fields = ('id', 'tipo_label', 'ciclo_anio', 'creado_en')
