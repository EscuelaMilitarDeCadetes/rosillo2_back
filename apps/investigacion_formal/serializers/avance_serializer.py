# apps/investigacion_formal/serializers/avance_serializer.py
from rest_framework import serializers


class DetalleAvanceObjetivoSerializer(serializers.Serializer):
    objetivo_id = serializers.IntegerField()
    objetivo = serializers.CharField()
    clase = serializers.CharField()
    promedio_avance = serializers.FloatField()
    peso = serializers.FloatField()


class AvanceProyectoSerializer(serializers.Serializer):
    proyecto_id = serializers.IntegerField()
    avance_ponderado = serializers.FloatField()
    avance_tiempo = serializers.FloatField()
    avance_presupuestal = serializers.FloatField()
    detalle_por_objetivo = DetalleAvanceObjetivoSerializer(many=True)