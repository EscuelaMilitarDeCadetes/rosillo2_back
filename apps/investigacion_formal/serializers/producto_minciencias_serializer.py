from rest_framework import serializers

from apps.investigacion_formal.models import ProductoMinciencias


class ProductoMincienciasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoMinciencias
        fields = '__all__'