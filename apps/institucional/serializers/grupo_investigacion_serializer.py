from rest_framework import serializers
from apps.institucional.models import GrupoInvestigacion


class GrupoInvestigacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoInvestigacion
        fields = '__all__'