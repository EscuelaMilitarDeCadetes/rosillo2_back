# apps/investigacion_formativa/serializers/banco_ideas_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import BancoIdeas


class BancoIdeasSerializer(serializers.ModelSerializer):

    facultad_nombre = serializers.CharField(
        source='facultad.nombre_facultad',
        read_only=True,
    )

    class Meta:
        model = BancoIdeas
        fields = '__all__'