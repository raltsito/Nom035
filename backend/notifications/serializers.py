from rest_framework import serializers
from .models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    tipo_label = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model  = Notificacion
        fields = ('id', 'tipo', 'tipo_label', 'titulo', 'mensaje',
                  'leida', 'url_destino', 'creado_en')
        read_only_fields = ('id', 'tipo', 'tipo_label', 'titulo', 'mensaje',
                            'url_destino', 'creado_en')
