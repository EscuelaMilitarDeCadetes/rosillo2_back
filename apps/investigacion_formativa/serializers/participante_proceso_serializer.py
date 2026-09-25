from rest_framework import serializers

from apps.investigacion_formativa.models import ParticipanteProceso


class ParticipanteProcesoSerializer(serializers.ModelSerializer):
    proceso_formativo_titulo = serializers.CharField(
        source='proceso_formativo.titulo',
        read_only=True
    )
    persona_documento = serializers.CharField(
        source='persona.documento',
        read_only=True
    )
    persona_nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = ParticipanteProceso
        fields = '__all__'

    def get_persona_nombre_completo(self, obj):
        persona = obj.persona
        return f"{persona.nombre} {persona.apellido}"