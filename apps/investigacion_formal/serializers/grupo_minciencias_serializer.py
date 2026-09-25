from rest_framework import serializers

from apps.investigacion_formal.models import GrupoMinciencias


class GrupoMincienciasSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoMinciencias
        fields = '__all__'