from rest_framework import serializers
from apps.common.models import Aprobacion


class AprobacionSerializer(serializers.ModelSerializer):
    tipo_documento_nombre = serializers.CharField(
        source='tipo_documento.nombre_documento',
        read_only=True
    )
    usuario_revisor = serializers.CharField(
        source='usuario_revisor.email',
        read_only=True
    )

    class Meta:
        model = Aprobacion
        fields = '__all__'
