from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    guias_aplicables = serializers.ReadOnlyField()
    categoria_tamano = serializers.ReadOnlyField()

    class Meta:
        model = Tenant
        fields = (
            'id', 'nombre', 'rfc', 'giro', 'num_trabajadores',
            'guias_aplicables', 'categoria_tamano', 'consultor',
            'activo', 'logo_url', 'sitio_web', 'telefono_contacto', 'direccion',
            'creado_en', 'actualizado_en',
        )
        read_only_fields = ('id', 'consultor', 'creado_en', 'actualizado_en',
                            'guias_aplicables', 'categoria_tamano')


class TenantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ('nombre', 'rfc', 'giro', 'num_trabajadores')

    def validate_rfc(self, value):
        return value.upper().strip()

    def create(self, validated_data):
        validated_data['consultor'] = self.context['request'].user
        return super().create(validated_data)


class TenantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ('nombre', 'giro', 'num_trabajadores', 'activo')

    def validate_rfc(self, value):
        return value.upper().strip()


class TenantBrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tenant
        fields = ('id', 'nombre', 'rfc', 'giro', 'num_trabajadores',
                  'logo_url', 'sitio_web', 'telefono_contacto', 'direccion')
        read_only_fields = ('id', 'nombre', 'rfc')
