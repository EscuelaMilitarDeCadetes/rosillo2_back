from rest_framework import serializers
from apps.common.models import Historial


class HistorialSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(
        source='usuario.username',
        read_only=True,
        default=None,
    )
    usuario_persona_documento = serializers.SerializerMethodField()
    objeto_tipo = serializers.SerializerMethodField()
    objeto_descripcion = serializers.SerializerMethodField()

    class Meta:
        model = Historial
        fields = '__all__'

    def get_usuario_persona_documento(self, obj):
        if not obj.usuario:
            return None
        asignacion = obj.usuario.asignaciones.filter(estado=True).first()
        return asignacion.persona.documento if asignacion else None

    def get_objeto_tipo(self, obj):
        return obj.content_type.model if obj.content_type else None

    def get_objeto_descripcion(self, obj):
        return str(obj.objeto_relacionado) if obj.objeto_relacionado else None