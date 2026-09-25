from rest_framework import serializers

from apps.investigacion_formal.models import Monto


class MontoSerializer(serializers.ModelSerializer):
    proyecto_titulo = serializers.CharField(
        source='proyecto.titulo',
        read_only=True
    )
    proyecto_codigo = serializers.CharField(
        source='proyecto.codigo',
        read_only=True
    )
    saldo_disponible = serializers.SerializerMethodField()

    class Meta:
        model = Monto
        fields = '__all__'

    def get_saldo_disponible(self, obj):
        aprobado = obj.aprobado or 0
        ejecutado = obj.ejecutado or 0
        return aprobado - ejecutado