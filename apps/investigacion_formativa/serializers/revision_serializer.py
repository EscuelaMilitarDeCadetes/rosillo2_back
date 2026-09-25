from rest_framework import serializers

from apps.investigacion_formativa.models import Revision


class RevisionSerializer(serializers.ModelSerializer):
    instancia_etapa_etapa = serializers.CharField(
        source='instancia_etapa.etapa.nombre',
        read_only=True
    )

    class Meta:
        model = Revision
        fields = '__all__'