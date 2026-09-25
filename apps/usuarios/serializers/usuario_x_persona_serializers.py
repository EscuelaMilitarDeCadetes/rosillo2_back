from rest_framework import serializers
from apps.usuarios.models import UsuarioXPersona


class UsuarioXPersonaSerializer(serializers.ModelSerializer):
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    persona_id = serializers.IntegerField(source='persona.id', read_only=True)
    persona_nombre = serializers.SerializerMethodField()

    class Meta:
        model = UsuarioXPersona
        fields = [
            'id', 'usuario_id', 'usuario_username',
            'persona_id', 'persona_nombre',
            'fecha_inicio', 'fecha_fin', 'estado'
        ]

    def get_persona_nombre(self, obj):
        # corregido: antes la fuente era 'persona.documento' pese a llamarse
        # 'persona_nombre'. Se calcula explícitamente el nombre completo.
        return f"{obj.persona.nombre} {obj.persona.apellido}"
