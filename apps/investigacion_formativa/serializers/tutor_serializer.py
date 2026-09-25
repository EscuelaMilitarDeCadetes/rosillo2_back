from rest_framework import serializers

from apps.investigacion_formativa.models import Tutor


class TutorSerializer(serializers.ModelSerializer):
    persona_documento = serializers.CharField(
        source='persona.documento',
        read_only=True
    )
    facultad_nombre = serializers.CharField(
        source='facultad.nombre_facultad',
        read_only=True
    )
    persona_nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Tutor
        fields = '__all__'

    def get_persona_nombre_completo(self, obj):
        persona = obj.persona
        return f"{persona.nombre} {persona.apellido}"