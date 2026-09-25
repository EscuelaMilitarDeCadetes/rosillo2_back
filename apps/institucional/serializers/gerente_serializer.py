from rest_framework import serializers
from apps.institucional.models import Gerente


class GerenteSerializer(serializers.ModelSerializer):
    persona_nombre = serializers.SerializerMethodField()
    persona_documento = serializers.CharField(
        source='persona.documento',
        read_only=True
    )

    class Meta:
        model = Gerente
        fields = '__all__'

    def get_persona_nombre(self, obj):
        if obj.persona_id is None:
            return None
        return f"{obj.persona.nombre} {obj.persona.apellido}"