# apps/investigacion_formativa/serializers/flujo_proceso_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import FlujoProceso


class FlujoProcesoSerializer(serializers.ModelSerializer):

    modalidad_nombre = serializers.CharField(
        source='modalidad_nombre',
        read_only=True,
    )

    class Meta:
        model = FlujoProceso
        fields = '__all__'