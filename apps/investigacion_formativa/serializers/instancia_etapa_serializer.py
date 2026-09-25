# apps/investigacion_formativa/serializers/instancia_etapa_serializer.py
from rest_framework import serializers

from apps.investigacion_formativa.models import InstanciaEtapa
from apps.investigacion_formativa.validators.instancia_etapa_validator import (
    TRANSICIONES_PERMITIDAS,
)


class InstanciaEtapaSerializer(serializers.ModelSerializer):

    proceso_titulo = serializers.CharField(
        source='proceso.titulo',
        read_only=True,
    )
    etapa_nombre = serializers.CharField(
        source='etapa.nombre',
        read_only=True,
    )
    # El serializer expone directamente la lista de transiciones válidas
    # para el estado actual de cada instancia, y el frontend simplemente
    # la consume en vez de recalcularla.
    transiciones_permitidas = serializers.SerializerMethodField()

    class Meta:
        model = InstanciaEtapa
        fields = '__all__'

    def get_transiciones_permitidas(self, obj):
        return list(TRANSICIONES_PERMITIDAS.get(obj.estado, ()))