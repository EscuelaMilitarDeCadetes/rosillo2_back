from rest_framework import serializers

from apps.investigacion_formativa.models import ValidacionAntiplagio


class ValidacionAntiplagioSerializer(serializers.ModelSerializer):
    instancia_etapa_etapa = serializers.CharField(
        source='instancia_etapa.etapa.nombre',
        read_only=True
    )
    documento_nombre_documento = serializers.CharField(
        source='documento.tipo_documento.nombre_documento',
        read_only=True
    )

    class Meta:
        model = ValidacionAntiplagio
        fields = '__all__'