from rest_framework import serializers

from apps.investigacion_formativa.models import ProcesoFormativoXProyecto


class ProcesoFormativoXProyectoSerializer(serializers.ModelSerializer):
    proceso_formativo_titulo = serializers.CharField(
        source='proceso_formativo.titulo',
        read_only=True
    )
    proyecto_formal_titulo = serializers.CharField(
        source='proyecto_formal.titulo',
        read_only=True
    )

    class Meta:
        model = ProcesoFormativoXProyecto
        fields = '__all__'