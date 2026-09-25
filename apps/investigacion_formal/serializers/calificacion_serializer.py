from rest_framework import serializers

from apps.investigacion_formal.models import Calificacion


class CalificacionSerializer(serializers.ModelSerializer):
    fase_nombre = serializers.CharField(
        source='fase.tipo_calificacion',
        read_only=True
    )
    fase_orden = serializers.IntegerField(
        source='fase.orden_fase',
        read_only=True
    )
    fase_es_evaluacion = serializers.BooleanField(
        source='fase.evaluacion',
        read_only=True
    )
    aplicar_proyecto_titulo = serializers.CharField(
        source='aplicar.proyecto.titulo',
        read_only=True
    )
    aplicar_convocatoria_nombre = serializers.CharField(
        source='aplicar.convocatoria.nombre_convocatoria',
        read_only=True
    )

    class Meta:
        model = Calificacion
        fields = '__all__'