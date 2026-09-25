from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector
from rest_framework import serializers

from apps.investigacion_formal.models import Proyecto


class ProyectoSerializer(serializers.ModelSerializer):
    tiene_acta_inicio = serializers.SerializerMethodField()
    
    usuario_username = serializers.CharField(
        source='usuario.username',
        read_only=True
    )
    gerente_nombre = serializers.SerializerMethodField()
    grupo_investigacion_nombre = serializers.CharField(
        source='grupo_investigacion.nombre_grupo', 
        read_only=True, default=None
    )
    facultad_nombre = serializers.CharField(
        source='facultad.nombre_facultad', 
        read_only=True, default=None
    )
    
    def get_tiene_acta_inicio(self, obj):
        return ProyectoSelector.tiene_acta_inicio(obj.pk)

    class Meta:
        model = Proyecto
        fields = '__all__'

    def get_gerente_nombre(self, obj):
        persona = obj.gerente.persona
        if persona is None:
            return None
        return f"{persona.nombre} {persona.apellido}"