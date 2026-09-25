from rest_framework import serializers

from apps.investigacion_formativa.models import RegistroHoras


class RegistroHorasSerializer(serializers.ModelSerializer):
    proceso_titulo = serializers.CharField(
        source='proceso.titulo',
        read_only=True
    )
    horas_pendientes = serializers.SerializerMethodField()

    class Meta:
        model = RegistroHoras
        fields = '__all__'

    def get_horas_pendientes(self, obj):
        pendientes = obj.horas_requeridas - obj.horas_acumuladas
        return max(pendientes, 0)