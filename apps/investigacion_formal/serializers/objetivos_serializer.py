from rest_framework import serializers

from apps.investigacion_formal.models import Objetivos


class ObjetivosSerializer(serializers.ModelSerializer):
    proyecto_titulo = serializers.CharField(
        source='proyecto.titulo',
        read_only=True
    )

    class Meta:
        model = Objetivos
        fields = '__all__'