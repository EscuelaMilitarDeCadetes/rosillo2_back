from rest_framework import serializers
from apps.institucional.models import Persona


class PersonaSerializer(serializers.ModelSerializer):
    grado_sigla = serializers.CharField(
        source='grado.sigla_grado',
        read_only=True
    )

    class Meta:
        model = Persona
        fields = '__all__'