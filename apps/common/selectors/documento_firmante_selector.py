from apps.common.models import DocumentoFirmante


class DocumentoFirmanteSelector:
    @staticmethod
    def listar():
        return DocumentoFirmante.objects.select_related('documento_firma', 'usuario').all()

    @staticmethod
    def obtener(documento_firmante_id):
        return (
            DocumentoFirmante.objects
            .select_related('documento_firma', 'usuario')
            .get(pk=documento_firmante_id)
        )

    @staticmethod
    def listar_por_documento(documento_firma_id):
        return (
            DocumentoFirmante.objects
            .select_related('usuario')
            .filter(documento_firma_id=documento_firma_id)
            .order_by('orden')
        )

    @staticmethod
    def listar_pendientes_por_usuario(usuario_id):
        return (DocumentoFirmante.objects.select_related('documento_firma', 'documento_firma__tipo_documento').filter(usuario_id=usuario_id, estado='PENDIENTE').order_by('documento_firma_id', 'orden'))

    @staticmethod
    def obtener_siguiente_turno(documento_firma_id):
        return (
            DocumentoFirmante.objects
            .filter(documento_firma_id=documento_firma_id, estado='PENDIENTE')
            .order_by('orden')
            .first()
        )

    @staticmethod
    def todos_firmaron(documento_firma_id):
        return not (
            DocumentoFirmante.objects
            .filter(documento_firma_id=documento_firma_id)
            .exclude(estado='FIRMADO')
            .exists()
        )

    @staticmethod
    def existe_firmante(documento_firma_id, usuario_id, excluir_id=None):
        qs = DocumentoFirmante.objects.filter(
            documento_firma_id=documento_firma_id, usuario_id=usuario_id
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()