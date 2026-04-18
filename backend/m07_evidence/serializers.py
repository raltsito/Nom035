from rest_framework import serializers
from .models import EvidenciaDocumento


class EvidenciaDocumentoSerializer(serializers.ModelSerializer):
    modulo_label    = serializers.CharField(source='get_modulo_display', read_only=True)
    ciclo_anio      = serializers.IntegerField(source='ciclo.anio', read_only=True)
    archivo_url     = serializers.SerializerMethodField()
    subido_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model  = EvidenciaDocumento
        fields = (
            'id', 'ciclo', 'ciclo_anio', 'modulo', 'modulo_label',
            'nombre', 'descripcion', 'archivo', 'archivo_url',
            'tamanio', 'tipo_mime', 'subido_por_nombre', 'creado_en',
        )
        read_only_fields = ('id', 'modulo_label', 'ciclo_anio', 'archivo_url',
                            'tamanio', 'tipo_mime', 'subido_por_nombre', 'creado_en')
        extra_kwargs = {'archivo': {'write_only': True}}

    def get_archivo_url(self, obj):
        request = self.context.get('request')
        if obj.archivo and request:
            return request.build_absolute_uri(obj.archivo.url)
        return None

    def get_subido_por_nombre(self, obj):
        if obj.subido_por:
            return obj.subido_por.get_full_name() or obj.subido_por.email
        return None
