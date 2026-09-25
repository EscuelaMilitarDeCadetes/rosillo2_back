from apps.common.models import DocumentoFirma
from django.contrib.contenttypes.models import ContentType


class DocumentoFirmaSelector:
    @staticmethod
    def listar():
        return DocumentoFirma.objects.select_related('tipo_documento').all()

    @staticmethod
    def obtener(documento_firma_id):
        return DocumentoFirma.objects.select_related('tipo_documento').get(pk=documento_firma_id)

    @staticmethod
    def buscar(documento_firma_id):
        return DocumentoFirma.objects.select_related('tipo_documento').filter(pk=documento_firma_id).first()

    @staticmethod
    def listar_por_tipo_documento(tipo_documento_id):
        return (
            DocumentoFirma.objects
            .filter(tipo_documento_id=tipo_documento_id)
            .order_by('-version')
        )

    @staticmethod
    def obtener_ultima_version(tipo_documento_id, objeto=None):
        qs = DocumentoFirma.objects.filter(
            tipo_documento_id=tipo_documento_id
        )
        if objeto is not None:
            content_type = ContentType.objects.get_for_model(objeto)
            qs = qs.filter(
                content_type=content_type,
                object_id=objeto.pk
            )
        return qs.order_by("-version").first()

    @staticmethod
    def listar_habilitados_para_firma():
        return (
            DocumentoFirma.objects
            .select_related('tipo_documento')
            .filter(habilitado_firma=True, estado='EN_FIRMAS')
        )

    @staticmethod
    def existe_version(tipo_documento_id, content_type, object_id, version, excluir_id=None):
        qs = DocumentoFirma.objects.filter(
            tipo_documento_id=tipo_documento_id, 
            content_type=content_type,
            object_id=object_id, 
            version=version
            )        
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
    
    @staticmethod
    def listar_por_objeto(objeto):        
        content_type = ContentType.objects.get_for_model(objeto)
        return (
            DocumentoFirma.objects
            .select_related('tipo_documento')
            .filter(content_type=content_type, object_id=objeto.pk)
            .order_by('-version')
        )
    
    @staticmethod
    def listar_para_verificar_integridad():
        """
        Todos los documentos con archivo físico registrado, sin importar
        su estado — un BORRADOR o un EN_FIRMAS también pueden ser
        alterados fuera de la plataforma, no solo los ya FIRMADOS.
        """
        return DocumentoFirma.objects.exclude(ruta_documento='')