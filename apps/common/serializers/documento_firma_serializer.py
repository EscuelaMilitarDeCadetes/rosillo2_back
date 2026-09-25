from rest_framework import serializers
from apps.common.models import DocumentoFirma


class DocumentoFirmaSerializer(serializers.ModelSerializer):
    tipo_documento_nombre = serializers.CharField(
        source='tipo_documento.nombre_documento',
        read_only=True
    )
    objeto_tipo = serializers.SerializerMethodField()
    objeto_id = serializers.IntegerField(source='object_id', read_only=True)
    objeto_descripcion = serializers.SerializerMethodField()
    tiene_firmantes = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoFirma
        fields = '__all__'
        # content_type/object_id se exponen solo en lectura, de forma legible;
        # la asociación se hace desde el Service (DocumentoFirmaService.crear)
        read_only_fields = ('content_type', 'object_id')

    def get_objeto_tipo(self, obj):
        return obj.content_type.model if obj.content_type else None

    def get_objeto_descripcion(self, obj):
        return str(obj.objeto_relacionado) if obj.objeto_relacionado else None
    
    def get_tiene_firmantes(self, obj):
        return obj.documentofirmante_set.exists()