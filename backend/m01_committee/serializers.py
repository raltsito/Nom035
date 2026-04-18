from rest_framework import serializers
from .models import ComiteNOM, MiembroComite, CapacitacionDC3


class CapacitacionDC3Serializer(serializers.ModelSerializer):
    class Meta:
        model  = CapacitacionDC3
        fields = ('id', 'miembro', 'tipo_capacitacion', 'fecha', 'horas', 'instructor', 'numero_dc3')
        read_only_fields = ('id',)


class MiembroComiteSerializer(serializers.ModelSerializer):
    capacitaciones = CapacitacionDC3Serializer(many=True, read_only=True)
    tipo_label     = serializers.CharField(source='get_tipo_display', read_only=True)
    total_dc3      = serializers.SerializerMethodField()

    class Meta:
        model  = MiembroComite
        fields = (
            'id', 'comite', 'nombre', 'puesto', 'tipo', 'tipo_label',
            'email', 'telefono', 'activo', 'capacitaciones', 'total_dc3',
        )
        read_only_fields = ('id', 'capacitaciones', 'tipo_label', 'total_dc3')

    def get_total_dc3(self, obj):
        return obj.capacitaciones.count()


class ComiteNOMSerializer(serializers.ModelSerializer):
    miembros       = MiembroComiteSerializer(many=True, read_only=True)
    ciclo_anio     = serializers.IntegerField(source='ciclo.anio', read_only=True)
    total_miembros = serializers.SerializerMethodField()

    class Meta:
        model  = ComiteNOM
        fields = (
            'id', 'ciclo', 'ciclo_anio', 'fecha_constitucion',
            'numero_acta', 'observaciones', 'miembros', 'total_miembros',
            'creado_en',
        )
        read_only_fields = ('id', 'miembros', 'ciclo_anio', 'total_miembros', 'creado_en')

    def get_total_miembros(self, obj):
        return obj.miembros.filter(activo=True).count()
