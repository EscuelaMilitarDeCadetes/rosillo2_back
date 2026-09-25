from rest_framework import serializers

from apps.investigacion_formativa.models import SegundaInstancia


class SegundaInstanciaSerializer(serializers.ModelSerializer):
    proceso_titulo = serializers.CharField(
        source='proceso.titulo',
        read_only=True
    )
    instancia_etapa_etapa = serializers.CharField(
        source='instancia_etapa.etapa.nombre',
        read_only=True
    )
    evaluacion_concepto = serializers.CharField(
        source='evaluacion.concepto',
        read_only=True
    )
    etapa_retorno_nombre = serializers.CharField(
        source='etapa_retorno.nombre',
        read_only=True
    )

    class Meta:
        model = SegundaInstancia
        fields = '__all__'