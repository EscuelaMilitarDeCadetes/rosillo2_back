from rest_framework import serializers

from apps.investigacion_formativa.models import RequisitoModalidad


class RequisitoModalidadSerializer(serializers.ModelSerializer):
    modalidad_nombre = serializers.CharField(
        source='modalidad.nombre',
        read_only=True
    )

    class Meta:
        model = RequisitoModalidad
        fields = '__all__'