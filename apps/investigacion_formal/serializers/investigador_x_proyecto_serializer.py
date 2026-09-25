from rest_framework import serializers

from apps.investigacion_formal.models import InvestigadorXProyecto


class InvestigadorXProyectoSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(
        source='rol_investigador.nombre_rol_investigador',
        read_only=True
    )
    proyecto_titulo = serializers.CharField(
        source='proyecto.titulo',
        read_only=True
    )
    persona_documento = serializers.CharField(
        source='persona_x_grupo.persona.documento',
        read_only=True
    )
    persona_nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = InvestigadorXProyecto
        fields = '__all__'

    def get_persona_nombre_completo(self, obj):
        persona = obj.persona_x_grupo.persona
        return f"{persona.nombre} {persona.apellido}"