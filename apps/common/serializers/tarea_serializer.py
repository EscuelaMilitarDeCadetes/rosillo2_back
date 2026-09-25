from rest_framework import serializers
from apps.common.models import Tarea


class TareaSerializer(serializers.ModelSerializer):
    asignado_a_username = serializers.CharField(
        source='asignado_a.username',
        read_only=True
    )
    objeto_tipo = serializers.SerializerMethodField()
    objeto_descripcion = serializers.SerializerMethodField()

    class Meta:
        model = Tarea
        fields = '__all__'

    def get_objeto_tipo(self, obj):
        return obj.content_type.model if obj.content_type else None

    def get_objeto_descripcion(self, obj):
        return str(obj.objeto_relacionado) if obj.objeto_relacionado else None