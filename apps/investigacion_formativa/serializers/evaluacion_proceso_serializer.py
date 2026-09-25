# apps/investigacion_formativa/serializers/evaluacion_proceso_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import EvaluacionProceso


class EvaluacionProcesoSerializer(serializers.ModelSerializer):

    evaluador_rol_en_modalidad = serializers.CharField(
        source='evaluador.rol_en_modalidad',
        read_only=True,
    )
    evaluador_nombre_completo = serializers.SerializerMethodField()
    instancia_etapa_etapa_nombre = serializers.CharField(
        source='instancia_etapa.etapa.nombre',
        read_only=True,
    )

    class Meta:
        model = EvaluacionProceso
        fields = '__all__'

    def get_evaluador_nombre_completo(self, obj):
        persona = obj.evaluador.persona
        return f"{persona.nombre} {persona.apellido}"