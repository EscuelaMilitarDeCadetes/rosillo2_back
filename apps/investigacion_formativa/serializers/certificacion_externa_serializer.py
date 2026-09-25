# apps/investigacion_formativa/serializers/certificacion_externa_serializer.py

from rest_framework import serializers

from apps.investigacion_formativa.models import CertificacionExterna


class CertificacionExternaSerializer(serializers.ModelSerializer):

    proceso_titulo = serializers.CharField(
        source='proceso.titulo',
        read_only=True,
    )
    certificado_asistencia_nombre = serializers.SerializerMethodField()
    certificado_aprobacion_nombre = serializers.SerializerMethodField()
    validado_por_username = serializers.SerializerMethodField()

    class Meta:
        model = CertificacionExterna
        fields = '__all__'

    def get_certificado_asistencia_nombre(self, obj):
        if not obj.certificado_asistencia_id:
            return None
        return obj.certificado_asistencia.tipo_documento.nombre_documento

    def get_certificado_aprobacion_nombre(self, obj):
        if not obj.certificado_aprobacion_id:
            return None
        return obj.certificado_aprobacion.tipo_documento.nombre_documento

    def get_validado_por_username(self, obj):
        if not obj.validado_por_id:
            return None
        return obj.validado_por.username