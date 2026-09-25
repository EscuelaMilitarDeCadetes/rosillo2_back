# apps/investigacion_formativa/serializers/etapa_flujo_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import EtapaFlujo


class EtapaFlujoSerializer(serializers.ModelSerializer):

    flujo_nombre = serializers.CharField(
        source='flujo.nombre',
        read_only=True,
    )
    documento_requerido_nombre = serializers.SerializerMethodField()

    class Meta:
        model = EtapaFlujo
        fields = '__all__'

    def get_documento_requerido_nombre(self, obj):
        if not obj.documento_requerido_id:
            return None
        return obj.documento_requerido.nombre_documento