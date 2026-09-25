from rest_framework import serializers

from apps.investigacion_formativa.models import PlanTrabajo


class PlanTrabajoSerializer(serializers.ModelSerializer):
    proceso_titulo = serializers.CharField(
        source='proceso.titulo',
        read_only=True
    )
    aprobado_por_username = serializers.CharField(
        source='aprobado_por.username',
        read_only=True
    )

    class Meta:
        model = PlanTrabajo
        fields = '__all__'