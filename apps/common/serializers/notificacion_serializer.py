from rest_framework import serializers
from apps.common.models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    usuario_destino = serializers.CharField(
        source='usuario_destino.email',
        read_only=True
    )

    class Meta:
        model = Notificacion
        fields = '__all__'