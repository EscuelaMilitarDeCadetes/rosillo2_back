from rest_framework import serializers
from apps.crm.models import IndicadorImpacto


class IndicadorImpactoSerializer(serializers.ModelSerializer):
    proyecto_titulo = serializers.CharField(
        source='proyecto.titulo',
        read_only=True
    )

    class Meta:
        model = IndicadorImpacto
        fields = '__all__'