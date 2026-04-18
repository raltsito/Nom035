from rest_framework import serializers
from .models import PlanAccion, AccionMedida


class AccionMedidaSerializer(serializers.ModelSerializer):
    tipo_label      = serializers.CharField(source='get_tipo_display',      read_only=True)
    prioridad_label = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_label    = serializers.CharField(source='get_estado_display',    read_only=True)
    vencida         = serializers.SerializerMethodField()

    class Meta:
        model  = AccionMedida
        fields = (
            'id', 'plan', 'descripcion', 'tipo', 'tipo_label',
            'factor_riesgo', 'responsable', 'fecha_limite',
            'prioridad', 'prioridad_label', 'estado', 'estado_label',
            'avance_notas', 'fecha_completado', 'vencida',
            'creado_en', 'actualizado_en',
        )
        read_only_fields = ('id', 'tipo_label', 'prioridad_label', 'estado_label', 'vencida', 'creado_en', 'actualizado_en')

    def get_vencida(self, obj):
        from datetime import date
        return (
            obj.estado not in ('completado', 'cancelado')
            and obj.fecha_limite < date.today()
        )


class PlanAccionSerializer(serializers.ModelSerializer):
    ciclo_anio  = serializers.IntegerField(source='ciclo.anio', read_only=True)
    stats       = serializers.SerializerMethodField()

    class Meta:
        model  = PlanAccion
        fields = ('id', 'ciclo', 'ciclo_anio', 'descripcion', 'creado_en', 'stats')
        read_only_fields = ('id', 'ciclo_anio', 'creado_en', 'stats')

    def get_stats(self, obj):
        acciones = obj.acciones.all()
        total        = acciones.count()
        completadas  = acciones.filter(estado='completado').count()
        en_progreso  = acciones.filter(estado='en_progreso').count()
        pendientes   = acciones.filter(estado='pendiente').count()
        canceladas   = acciones.filter(estado='cancelado').count()
        pct = round(completadas / total * 100) if total else 0
        return {
            'total':       total,
            'completadas': completadas,
            'en_progreso': en_progreso,
            'pendientes':  pendientes,
            'canceladas':  canceladas,
            'pct_avance':  pct,
        }
