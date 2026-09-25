# apps/investigacion_formativa/serializers/modalidad_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import Modalidad


class ModalidadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Modalidad
        fields = '__all__'