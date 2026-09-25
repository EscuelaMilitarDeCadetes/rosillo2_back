# apps/investigacion_formativa/serializers/homologacion_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import Homologacion


class HomologacionSerializer(serializers.ModelSerializer):

    proceso_titulo = serializers.CharField(
        source='proceso.titulo',
        read_only=True,
    )
    acta_homologacion_nombre = serializers.SerializerMethodField()
    aprobado_por_username = serializers.SerializerMethodField()

    class Meta:
        model = Homologacion
        fields = '__all__'

    def get_acta_homologacion_nombre(self, obj):
        if not obj.acta_homologacion_id:
            return None
        return obj.acta_homologacion.tipo_documento.nombre_documento

    def get_aprobado_por_username(self, obj):
        if not obj.aprobado_por_id:
            return None
        return obj.aprobado_por.username