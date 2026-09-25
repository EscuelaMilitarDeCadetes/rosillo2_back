# apps/investigacion_formativa/serializers/evento_evaluativo_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import EventoEvaluativo


class EventoEvaluativoSerializer(serializers.ModelSerializer):

    proceso_formativo_titulo = serializers.CharField(
        source='proceso_formativo.titulo',
        read_only=True,
    )
    acta_sustentacion_nombre = serializers.SerializerMethodField()

    class Meta:
        model = EventoEvaluativo
        fields = '__all__'

    def get_acta_sustentacion_nombre(self, obj):
        if not obj.acta_sustentacion_id:
            return None
        return obj.acta_sustentacion.tipo_documento.nombre_documento