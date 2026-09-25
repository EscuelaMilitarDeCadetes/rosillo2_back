# apps/investigacion_formativa/serializers/avance_serializer.py
from rest_framework import serializers


class EtapaActualSerializer(serializers.Serializer):
    instancia_id = serializers.IntegerField()
    etapa_id = serializers.IntegerField()
    etapa_nombre = serializers.CharField()
    orden = serializers.IntegerField()
    estado = serializers.CharField()
    fecha_inicio = serializers.DateTimeField(allow_null=True)


class UltimoRegistroAvanceSerializer(serializers.Serializer):
    registro_id = serializers.IntegerField()
    tipo_periodo = serializers.CharField()
    fecha_periodo = serializers.DateField()
    horas_reportadas = serializers.FloatField()
    aprobado = serializers.BooleanField()


class AvanceProcesoFormativoSerializer(serializers.Serializer):
    """Serializa la salida compuesta del service de avance de un ProcesoFormativo."""
    proceso_id = serializers.IntegerField()
    porcentaje_avance = serializers.FloatField(allow_null=True)
    avance_tiempo = serializers.FloatField(allow_null=True)
    horas_acumuladas = serializers.FloatField(allow_null=True)
    etapas_aprobadas = serializers.IntegerField()
    etapas_totales = serializers.IntegerField()
    en_segunda_instancia = serializers.BooleanField()
    etapa_actual = EtapaActualSerializer(allow_null=True)
    ultimo_registro = UltimoRegistroAvanceSerializer(allow_null=True)