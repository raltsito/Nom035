from rest_framework import serializers
from .models import ResultadoAplicacion, ResultadoDominio


class ResultadoDominioSerializer(serializers.ModelSerializer):
    dominio_clave  = serializers.CharField(source='dominio.clave',  read_only=True)
    dominio_nombre = serializers.CharField(source='dominio.nombre', read_only=True)
    porcentaje     = serializers.SerializerMethodField()

    class Meta:
        model  = ResultadoDominio
        fields = ['id', 'dominio_clave', 'dominio_nombre',
                  'puntaje', 'puntaje_max', 'porcentaje', 'categoria']

    def get_porcentaje(self, obj):
        if obj.puntaje_max == 0:
            return 0
        return round(obj.puntaje / obj.puntaje_max * 100)


class ResultadoAplicacionSerializer(serializers.ModelSerializer):
    trabajador_nombre   = serializers.CharField(
        source='aplicacion.trabajador.nombre_completo', read_only=True)
    trabajador_area     = serializers.CharField(
        source='aplicacion.trabajador.area', read_only=True)
    cuestionario_clave  = serializers.CharField(
        source='aplicacion.cuestionario.clave', read_only=True)
    ciclo               = serializers.IntegerField(
        source='aplicacion.ciclo_id', read_only=True)
    porcentaje          = serializers.SerializerMethodField()
    dominios            = ResultadoDominioSerializer(many=True, read_only=True)

    class Meta:
        model  = ResultadoAplicacion
        fields = [
            'id', 'aplicacion', 'trabajador_nombre', 'trabajador_area',
            'cuestionario_clave', 'ciclo',
            'puntaje_total', 'puntaje_max', 'porcentaje',
            'categoria', 'calculado_en', 'dominios',
        ]

    def get_porcentaje(self, obj):
        if obj.puntaje_max == 0:
            return 0
        return round(obj.puntaje_total / obj.puntaje_max * 100)


class ResultadoListSerializer(ResultadoAplicacionSerializer):
    """Lista sin el detalle de dominios para la tabla principal."""
    class Meta(ResultadoAplicacionSerializer.Meta):
        fields = [
            'id', 'aplicacion', 'trabajador_nombre', 'trabajador_area',
            'cuestionario_clave', 'ciclo',
            'puntaje_total', 'puntaje_max', 'porcentaje', 'categoria', 'calculado_en',
        ]
