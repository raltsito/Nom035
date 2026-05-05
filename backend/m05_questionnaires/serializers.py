from rest_framework import serializers
from .models import Cuestionario, Dominio, Pregunta, Aplicacion, RespuestaPregunta, GuiaLink


class PreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Pregunta
        fields = ['id', 'orden', 'texto', 'inversa']


class DominioSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True)

    class Meta:
        model  = Dominio
        fields = ['id', 'orden', 'clave', 'nombre', 'preguntas']


class CuestionarioSerializer(serializers.ModelSerializer):
    dominios = DominioSerializer(many=True, read_only=True)
    total_preguntas = serializers.SerializerMethodField()

    class Meta:
        model  = Cuestionario
        fields = ['id', 'clave', 'nombre', 'descripcion', 'tamano_min', 'tamano_max', 'dominios', 'total_preguntas']

    def get_total_preguntas(self, obj):
        return Pregunta.objects.filter(dominio__cuestionario=obj).count()


class CuestionarioListSerializer(serializers.ModelSerializer):
    total_preguntas = serializers.SerializerMethodField()

    class Meta:
        model  = Cuestionario
        fields = ['id', 'clave', 'nombre', 'tamano_min', 'tamano_max', 'total_preguntas']

    def get_total_preguntas(self, obj):
        return Pregunta.objects.filter(dominio__cuestionario=obj).count()


class AplicacionSerializer(serializers.ModelSerializer):
    trabajador_nombre    = serializers.CharField(source='trabajador.nombre_completo', read_only=True)
    trabajador_area      = serializers.CharField(source='trabajador.area', read_only=True)
    trabajador_puesto    = serializers.CharField(source='trabajador.puesto', read_only=True)
    cuestionario_clave   = serializers.CharField(source='cuestionario.clave', read_only=True)
    cuestionario_nombre  = serializers.CharField(source='cuestionario.nombre', read_only=True)
    total_preguntas      = serializers.SerializerMethodField()
    total_respondidas    = serializers.SerializerMethodField()

    class Meta:
        model  = Aplicacion
        fields = [
            'id', 'ciclo', 'cuestionario', 'cuestionario_clave', 'cuestionario_nombre',
            'trabajador', 'trabajador_nombre', 'trabajador_area', 'trabajador_puesto',
            'estado', 'token', 'fecha_completado',
            'total_preguntas', 'total_respondidas',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'token', 'estado', 'fecha_completado', 'creado_en', 'actualizado_en']

    def get_total_preguntas(self, obj):
        return Pregunta.objects.filter(dominio__cuestionario=obj.cuestionario).count()

    def get_total_respondidas(self, obj):
        return obj.respuestas.count()


class RespuestaPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RespuestaPregunta
        fields = ['id', 'pregunta', 'valor']


class SubmitRespuestasSerializer(serializers.Serializer):
    """Recibe todas las respuestas del cuestionario en un solo POST."""
    respuestas = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        min_length=1,
    )

    def validate_respuestas(self, value):
        for item in value:
            if 'pregunta_id' not in item or 'valor' not in item:
                raise serializers.ValidationError('Cada respuesta debe tener pregunta_id y valor.')
            if item['valor'] not in range(5):
                raise serializers.ValidationError('El valor debe estar entre 0 y 4.')
        return value


class GuiaLinkSerializer(serializers.ModelSerializer):
    cuestionario_clave  = serializers.CharField(source='cuestionario.clave', read_only=True)
    cuestionario_nombre = serializers.CharField(source='cuestionario.nombre', read_only=True)

    class Meta:
        model  = GuiaLink
        fields = [
            'id', 'ciclo', 'cuestionario', 'cuestionario_clave', 'cuestionario_nombre',
            'token', 'activo', 'creado_en',
        ]
        read_only_fields = ['id', 'token', 'creado_en']


class GuiaLinkPublicaSerializer(serializers.ModelSerializer):
    cuestionario_clave  = serializers.CharField(source='cuestionario.clave', read_only=True)
    cuestionario_nombre = serializers.CharField(source='cuestionario.nombre', read_only=True)

    class Meta:
        model  = GuiaLink
        fields = ['cuestionario_clave', 'cuestionario_nombre', 'token', 'activo']


class AplicacionPublicaSerializer(serializers.ModelSerializer):
    """Datos publicos de una aplicacion para la pantalla de respuesta."""
    trabajador_nombre   = serializers.CharField(source='trabajador.nombre_completo', read_only=True)
    cuestionario        = CuestionarioSerializer(read_only=True)
    respuestas_guardadas = serializers.SerializerMethodField()

    class Meta:
        model  = Aplicacion
        fields = [
            'id', 'estado', 'token',
            'trabajador_nombre', 'cuestionario',
            'respuestas_guardadas',
        ]

    def get_respuestas_guardadas(self, obj):
        return {str(r.pregunta_id): r.valor for r in obj.respuestas.all()}
