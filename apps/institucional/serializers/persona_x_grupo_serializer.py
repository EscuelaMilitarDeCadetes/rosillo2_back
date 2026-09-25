from rest_framework import serializers
from apps.institucional.models import PersonaXGrupo


class PersonaXGrupoSerializer(serializers.ModelSerializer):
    persona_nombre = serializers.SerializerMethodField()
    persona_documento = serializers.CharField(
        source='persona.documento',
        read_only=True
    )
    rol_grupo_nombre = serializers.CharField(
        source='rol_grupo.cargo',
        read_only=True
    )
    grupo_nombre = serializers.CharField(
        source='grupo.sigla_grupo',
        read_only=True
    )
    facultad_nombre = serializers.CharField(
        source='facultad.abreviatura',
        read_only=True
    )

    class Meta:
        model = PersonaXGrupo
        fields = '__all__'

    def get_persona_nombre(self, obj):
        if obj.persona_id is None:
            return None
        return f"{obj.persona.nombre} {obj.persona.apellido}"