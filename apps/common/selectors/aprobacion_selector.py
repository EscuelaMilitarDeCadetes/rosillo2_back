from apps.common.models import Aprobacion


class AprobacionSelector:
    @staticmethod
    def listar():
        return Aprobacion.objects.select_related('usuario_revisor', 'tipo_documento').all()

    @staticmethod
    def obtener(aprobacion_id):
        return Aprobacion.objects.select_related('usuario_revisor', 'tipo_documento').get(pk=aprobacion_id)

    @staticmethod
    def listar_pendientes(usuario_revisor_id=None):
        qs = Aprobacion.objects.select_related('tipo_documento').filter(estado='PENDIENTE')
        if usuario_revisor_id is not None:
            qs = qs.filter(usuario_revisor_id=usuario_revisor_id)
        return qs.order_by('-fecha_revision')

    @staticmethod
    def listar_por_documento(tipo_documento_id, id_documento):
        return (
            Aprobacion.objects
            .select_related('usuario_revisor')
            .filter(tipo_documento_id=tipo_documento_id, id_documento=id_documento)
            .order_by('-fecha_revision')
        )

    @staticmethod
    def obtener_ultima_por_documento(tipo_documento_id, id_documento):
        return (
            Aprobacion.objects
            .filter(tipo_documento_id=tipo_documento_id, id_documento=id_documento)
            .order_by('-fecha_revision')
            .first()
        )

    @staticmethod
    def existe_aprobacion(usuario_revisor_id, tipo_documento_id, id_documento, excluir_id=None):
        qs = Aprobacion.objects.filter(
            usuario_revisor_id=usuario_revisor_id,
            tipo_documento_id=tipo_documento_id,
            id_documento=id_documento,
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()