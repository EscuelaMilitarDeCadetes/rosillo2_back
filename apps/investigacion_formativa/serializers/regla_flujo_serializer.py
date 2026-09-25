from rest_framework import serializers

from apps.investigacion_formativa.models import ReglaFlujo


class ReglaFlujoSerializer(serializers.ModelSerializer):
    etapa_origen_nombre = serializers.CharField(
        source='etapa_origen.nombre',
        read_only=True
    )
    etapa_destino_nombre = serializers.CharField(
        source='etapa_destino.nombre',
        read_only=True
    )

    class Meta:
        model = ReglaFlujo
        fields = '__all__'