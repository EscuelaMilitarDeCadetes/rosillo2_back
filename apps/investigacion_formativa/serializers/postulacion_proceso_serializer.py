from rest_framework import serializers

from apps.investigacion_formativa.models import PostulacionProceso


class PostulacionProcesoSerializer(serializers.ModelSerializer):
    estudiante_persona_documento = serializers.CharField(
        source='estudiante.persona.documento',
        read_only=True
    )
    estudiante_nombre_completo = serializers.SerializerMethodField()
    modalidad_nombre = serializers.CharField(
        source='modalidad.modalidad.nombre',
        read_only=True
    )
    proceso_creado_titulo = serializers.SerializerMethodField()

    class Meta:
        model = PostulacionProceso
        fields = '__all__'

    def get_estudiante_nombre_completo(self, obj):
        persona = obj.estudiante.persona
        return f"{persona.nombre} {persona.apellido}"

    def get_proceso_creado_titulo(self, obj):
        if obj.proceso_creado is None:
            return None
        return obj.proceso_creado.titulo