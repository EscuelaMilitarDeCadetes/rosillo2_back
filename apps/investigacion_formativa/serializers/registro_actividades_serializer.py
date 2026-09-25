from rest_framework import serializers

from apps.investigacion_formativa.models import RegistroActividades


class RegistroActividadesSerializer(serializers.ModelSerializer):
    proceso_titulo = serializers.CharField(
        source='proceso.titulo',
        read_only=True
    )
    registrado_por_username = serializers.SerializerMethodField()
    documento_nombre_documento = serializers.SerializerMethodField()

    class Meta:
        model = RegistroActividades
        fields = '__all__'

    def get_registrado_por_username(self, obj):
        if obj.registrado_por is None:
            return None
        return obj.registrado_por.username

    def get_documento_nombre_documento(self, obj):
        if obj.documento is None:
            return None
        return obj.documento.tipo_documento.nombre_documento