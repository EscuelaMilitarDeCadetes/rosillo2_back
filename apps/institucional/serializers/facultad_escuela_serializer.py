from rest_framework import serializers
from apps.institucional.models import FacultadEscuela


class FacultadEscuelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultadEscuela
        fields = '__all__'