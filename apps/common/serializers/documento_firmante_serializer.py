from rest_framework import serializers
from apps.common.models import DocumentoFirmante


class DocumentoFirmanteSerializer(serializers.ModelSerializer):
    documento_firma_hash = serializers.CharField(
        source='documento_firma.hash_documento',
        read_only=True
    )
    usuario_username = serializers.CharField(
        source='usuario.username',
        read_only=True
    )
    usuario_persona_documento = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoFirmante
        fields = '__all__'
        # El código de verificación se envía por un canal aparte (email/sms);
        # exponerlo en la API anularía su propósito.
        extra_kwargs = {
            'codigo_verificacion': {'write_only': True},
        }

    def get_usuario_persona_documento(self, obj):
        asignacion = obj.usuario.asignaciones.filter(estado=True).first()
        return asignacion.persona.documento if asignacion else None