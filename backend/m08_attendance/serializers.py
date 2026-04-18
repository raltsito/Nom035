from rest_framework import serializers
from .models import Reunion, Asistente


class AsistenteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Asistente
        fields = ('id', 'reunion', 'nombre', 'puesto', 'firma_recibida', 'creado_en')
        read_only_fields = ('id', 'creado_en')


class ReunionSerializer(serializers.ModelSerializer):
    tipo_label      = serializers.CharField(source='get_tipo_display', read_only=True)
    ciclo_anio      = serializers.IntegerField(source='ciclo.anio', read_only=True)
    num_asistentes  = serializers.SerializerMethodField()
    asistentes      = AsistenteSerializer(many=True, read_only=True)

    class Meta:
        model  = Reunion
        fields = (
            'id', 'ciclo', 'ciclo_anio', 'tipo', 'tipo_label',
            'titulo', 'fecha', 'lugar', 'agenda', 'minuta',
            'num_asistentes', 'asistentes', 'creado_en', 'actualizado_en',
        )
        read_only_fields = ('id', 'tipo_label', 'ciclo_anio', 'num_asistentes',
                            'asistentes', 'creado_en', 'actualizado_en')

    def get_num_asistentes(self, obj):
        return obj.asistentes.count()
