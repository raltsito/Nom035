from rest_framework import serializers
from .models import (
    ResultadoAplicacion,
    ResultadoCategoria,
    ResultadoDimension,
    ResultadoDominio,
    ResultadoDominioOficial,
)


class ResultadoDominioSerializer(serializers.ModelSerializer):
    """Bloques internos de captura D1-D14: `categoria` es un semáforo
    referencial (no un nivel oficial de la NOM-035)."""
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


class ResultadoDominioOficialSerializer(serializers.ModelSerializer):
    dominio_clave  = serializers.CharField(source='clave',  read_only=True)
    dominio_nombre = serializers.CharField(source='nombre', read_only=True)
    porcentaje     = serializers.SerializerMethodField()

    class Meta:
        model  = ResultadoDominioOficial
        fields = ['id', 'dominio_clave', 'dominio_nombre',
                  'puntaje', 'puntaje_max', 'porcentaje', 'categoria']

    def get_porcentaje(self, obj):
        if obj.puntaje_max == 0:
            return 0
        return round(obj.puntaje / obj.puntaje_max * 100)


class ResultadoCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ResultadoCategoria
        fields = ['id', 'nombre', 'orden', 'puntaje', 'puntaje_max', 'categoria']


class ResultadoDimensionSerializer(serializers.ModelSerializer):
    """Dimensiones (Tabla 6): SOLO descriptivas — la NOM-035 no establece
    puntos de corte por dimensión, por lo que no llevan nivel."""
    class Meta:
        model  = ResultadoDimension
        fields = ['id', 'nombre', 'dominio_oficial', 'orden',
                  'puntaje', 'puntaje_max', 'pct']


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
    dominios_oficiales  = ResultadoDominioOficialSerializer(many=True, read_only=True)
    categorias          = ResultadoCategoriaSerializer(many=True, read_only=True)
    dimensiones         = ResultadoDimensionSerializer(many=True, read_only=True)

    class Meta:
        model  = ResultadoAplicacion
        fields = [
            'id', 'aplicacion', 'trabajador_nombre', 'trabajador_area',
            'cuestionario_clave', 'ciclo',
            'puntaje_total', 'puntaje_max', 'porcentaje',
            'categoria', 'requiere_atencion', 'calculado_en',
            'estatus_validacion', 'version_motor', 'hash_respuestas',
            'dominios', 'dominios_oficiales', 'categorias', 'dimensiones',
        ]

    def get_porcentaje(self, obj):
        if obj.puntaje_max == 0:
            return 0
        return round(obj.puntaje_total / obj.puntaje_max * 100)


class ResultadoListSerializer(ResultadoAplicacionSerializer):
    """Lista sin el detalle de dominios para la tabla principal."""
    trabajador_tipo_puesto = serializers.CharField(
        source='aplicacion.trabajador.tipo_puesto', read_only=True)

    class Meta(ResultadoAplicacionSerializer.Meta):
        fields = [
            'id', 'aplicacion', 'trabajador_nombre', 'trabajador_area',
            'trabajador_tipo_puesto', 'cuestionario_clave', 'ciclo',
            'puntaje_total', 'puntaje_max', 'porcentaje',
            'categoria', 'requiere_atencion', 'calculado_en',
            'estatus_validacion',
        ]
