from rest_framework import serializers
from apps.common.models import PlantillaDocumento


class PlantillaDocumentoSerializer(serializers.ModelSerializer):
    tipo_documento_nombre = serializers.CharField(
        source='tipo_documento.nombre_documento',
        read_only=True
    )

    class Meta:
        model = PlantillaDocumento
        fields = '__all__'