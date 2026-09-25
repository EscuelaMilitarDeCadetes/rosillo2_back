from rest_framework import serializers
from apps.institucional.models import GradoEstudios


class GradoEstudiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradoEstudios
        fields = '__all__'