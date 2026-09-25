# apps/investigacion_formativa/serializers/estudiante_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import Estudiante


class EstudianteSerializer(serializers.ModelSerializer):

    persona_documento = serializers.CharField(
        source='persona.documento',
        read_only=True,
    )
    persona_nombre_completo = serializers.SerializerMethodField()
    modalidad_facultad_nombre = serializers.CharField(
        source='modalidad_facultad.modalidad.nombre',
        read_only=True,
    )
    facultad_nombre = serializers.CharField(
        source='modalidad_facultad.facultad.nombre_facultad',
        read_only=True,
    )

    class Meta:
        model = Estudiante
        fields = '__all__'

    def get_persona_nombre_completo(self, obj):
        return f"{obj.persona.nombre} {obj.persona.apellido}"