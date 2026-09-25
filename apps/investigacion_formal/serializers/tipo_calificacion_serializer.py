from rest_framework import serializers

from apps.investigacion_formal.models import TipoCalificacion


class TipoCalificacionSerializer(serializers.ModelSerializer):
    ordenFase = serializers.IntegerField(source='orden_fase', read_only=True)
    class Meta:
        model = TipoCalificacion
        fields = '__all__'