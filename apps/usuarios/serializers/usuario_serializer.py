from rest_framework import serializers
from apps.usuarios.models import Usuario
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    # El source directo ya no existe. Usamos un SerializerMethodField.
    persona_actual_nombre = serializers.SerializerMethodField()
    persona_actual_documento = serializers.SerializerMethodField()
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True, default=None)

    class Meta:
        model = Usuario
        # Definimos los campos explícitamente para incluir los nuevos campos de método
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff',
            'persona_actual_nombre', 'persona_actual_documento',
            'creado_por', 'creado_por_username',
        ]
    
    def _persona_actual(self, obj):
        activas = [a for a in obj.asignaciones.all() if a.estado]
        return activas[0] if activas else None

    def get_persona_actual_nombre(self, obj):
        asignacion_activa = self._persona_actual(obj)
        if asignacion_activa:
            return f"{asignacion_activa.persona.nombre} {asignacion_activa.persona.apellido}"
        return None

    def get_persona_actual_documento(self, obj):
        asignacion_activa = self._persona_actual(obj)
        return asignacion_activa.persona.documento if asignacion_activa else None