from rest_framework import serializers

from apps.investigacion_formal.models import ControlCambios


class ControlCambiosSerializer(serializers.ModelSerializer):
    proyecto_titulo = serializers.CharField(
        source='proyecto.titulo',
        read_only=True
    )
    proyecto_codigo = serializers.CharField(
        source='proyecto.codigo',
        read_only=True
    )

    class Meta:
        model = ControlCambios
        fields = '__all__'