from rest_framework import serializers
from apps.crm.models import EntidadExterna


class EntidadExternaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntidadExterna
        fields = '__all__'