from rest_framework import serializers

from apps.investigacion_formal.models import TipoRubro


class TipoRubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRubro
        fields = '__all__'