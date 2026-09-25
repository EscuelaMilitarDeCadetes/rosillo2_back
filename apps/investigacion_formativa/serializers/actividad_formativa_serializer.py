# apps/investigacion_formativa/serializers/actividad_formativa_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import ActividadFormativa


class ActividadFormativaSerializer(serializers.ModelSerializer):

    proceso_formativo_titulo = serializers.CharField(
        source='proceso_formativo.titulo',
        read_only=True,
    )
    responsable_nombre_completo = serializers.SerializerMethodField()
    documento_soporte_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ActividadFormativa
        fields = '__all__'

    def get_responsable_nombre_completo(self, obj):
        if not obj.responsable_id:
            return None
        return f"{obj.responsable.nombre} {obj.responsable.apellido}"

    def get_documento_soporte_nombre(self, obj):
        if not obj.documento_soporte_id:
            return None
        return obj.documento_soporte.tipo_documento.nombre_documento