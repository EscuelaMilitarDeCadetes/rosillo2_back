# apps/investigacion_formativa/serializers/modalidad_x_facultad_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import ModalidadXFacultad


class ModalidadXFacultadSerializer(serializers.ModelSerializer):

    modalidad_nombre = serializers.CharField(
        source='modalidad.nombre',
        read_only=True,
    )
    facultad_nombre = serializers.CharField(
        source='facultad.nombre_facultad',
        read_only=True,
    )

    class Meta:
        model = ModalidadXFacultad
        fields = '__all__'