from rest_framework import serializers
from apps.crm.models import Interaccion


class InteraccionSerializer(serializers.ModelSerializer):
    entidad_nombre = serializers.CharField(
        source='entidad.nombre',
        read_only=True
    )
    proyecto_asociado_titulo = serializers.CharField(
        source='proyecto_asociado.titulo',
        read_only=True
    )

    class Meta:
        model = Interaccion
        fields = '__all__'