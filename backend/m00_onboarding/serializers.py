from rest_framework import serializers
from .models import Trabajador, CicloNOM


GUIA_V_FIELDS = [
    'sexo', 'edad', 'estado_civil', 'nivel_estudios',
    'tipo_puesto', 'tipo_personal', 'tipo_jornada', 'rotacion_turnos',
    'experiencia_anios', 'experiencia_empresa_anios', 'tiempo_puesto_actual',
]


class TrabajadorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model  = Trabajador
        fields = [
            'id', 'nombre', 'apellido_paterno', 'apellido_materno',
            'nombre_completo', 'num_empleado', 'email',
            'puesto', 'area', 'tipo_contratacion', 'activo',
            *GUIA_V_FIELDS,
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'nombre_completo', 'creado_en', 'actualizado_en']


class TrabajadorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Trabajador
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno',
            'num_empleado', 'email', 'puesto', 'area', 'tipo_contratacion',
            *GUIA_V_FIELDS,
        ]

    def create(self, validated_data):
        tenant = self.context['request'].user.tenant
        return Trabajador.objects.create(tenant=tenant, **validated_data)


class TrabajadorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Trabajador
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno',
            'num_empleado', 'email', 'puesto', 'area', 'tipo_contratacion', 'activo',
            *GUIA_V_FIELDS,
        ]


class CicloNOMSerializer(serializers.ModelSerializer):
    guias_aplicables = serializers.SerializerMethodField()
    total_trabajadores = serializers.SerializerMethodField()

    class Meta:
        model  = CicloNOM
        fields = [
            'id', 'anio', 'estado', 'fecha_inicio', 'fecha_cierre',
            'notas', 'guias_aplicables', 'total_trabajadores',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'guias_aplicables', 'total_trabajadores', 'creado_en', 'actualizado_en']

    def get_guias_aplicables(self, obj):
        return obj.tenant.guias_aplicables

    def get_total_trabajadores(self, obj):
        return Trabajador.objects.filter(tenant=obj.tenant, activo=True).count()


class CicloNOMCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CicloNOM
        fields = ['anio', 'fecha_inicio', 'notas']

    def validate_anio(self, value):
        tenant = self.context['request'].user.tenant
        if CicloNOM.objects.filter(tenant=tenant, anio=value).exists():
            raise serializers.ValidationError(f'Ya existe un ciclo para el año {value}.')
        return value

    def create(self, validated_data):
        tenant = self.context['request'].user.tenant
        return CicloNOM.objects.create(tenant=tenant, **validated_data)
