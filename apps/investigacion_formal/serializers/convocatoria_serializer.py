from django.utils import timezone
from rest_framework import serializers
from apps.investigacion_formal.models import Convocatoria
class ConvocatoriaSerializer(serializers.ModelSerializer):
    vigente_por_fechas = serializers.SerializerMethodField()
    class Meta:
        model = Convocatoria
        fields = '__all__'
    def get_vigente_por_fechas(self, obj):
        hoy = timezone.now().date()
        return obj.inicio <= hoy <= obj.cierre