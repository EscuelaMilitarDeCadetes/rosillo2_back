from rest_framework import serializers

from apps.investigacion_formal.models import Ejecucion


class EjecucionSerializer(serializers.ModelSerializer):
    monto_proyecto_titulo = serializers.CharField(
        source='monto.proyecto.titulo',
        read_only=True
    )
    monto_aprobado = serializers.FloatField(
        source='monto.aprobado',
        read_only=True
    )
    tipo_rubro_nombre = serializers.CharField(
        source='tipo_rubro.nombre_rubro',
        read_only=True
    )

    class Meta:
        model = Ejecucion
        fields = '__all__'