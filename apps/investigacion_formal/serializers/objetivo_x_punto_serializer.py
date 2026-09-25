from rest_framework import serializers

from apps.investigacion_formal.models import ObjetivoXPunto


class ObjetivoXPuntoSerializer(serializers.ModelSerializer):
    objetivo_texto = serializers.CharField(
        source='objetivo.objetivo',
        read_only=True
    )
    objetivo_proyecto_titulo = serializers.CharField(
        source='objetivo.proyecto.titulo',
        read_only=True
    )
    punto_control_control = serializers.CharField(
        source='punto_control.control',
        read_only=True
    )
    punto_control_peso = serializers.FloatField(
        source='punto_control.peso',
        read_only=True
    )

    class Meta:
        model = ObjetivoXPunto
        fields = '__all__'