from rest_framework import serializers

from apps.investigacion_formal.models import PuntoControl


class PuntoControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoControl
        fields = '__all__'