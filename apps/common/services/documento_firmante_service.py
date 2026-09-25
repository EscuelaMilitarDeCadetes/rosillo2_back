import secrets
from django.db import transaction
from apps.common.models import DocumentoFirmante
from apps.common.selectors.documento_firmante_selector import DocumentoFirmanteSelector
from apps.common.validators.documento_firmante_validator import DocumentoFirmanteValidator
from apps.common.services.historial_service import HistorialService
from apps.common.services.documento_firma_service import DocumentoFirmaService
from apps.common.services.notificacion_service import NotificacionService


class DocumentoFirmanteService:
    @staticmethod
    def listar():
        return DocumentoFirmanteSelector.listar()

    @staticmethod
    def obtener(documento_firmante_id):
        return DocumentoFirmanteSelector.obtener(documento_firmante_id)

    @staticmethod
    @transaction.atomic
    def asignar_firmante(documento_firma_id, usuario_id, orden, ejecutor):
        DocumentoFirmanteValidator.validar_creacion(documento_firma_id, usuario_id, orden)
        firmante = DocumentoFirmante.objects.create(
            documento_firma_id=documento_firma_id,
            usuario_id=usuario_id,
            orden=orden,
            estado='PENDIENTE',
            ip_firma='0.0.0.0',
            ruta_firma='',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se asignó al usuario id={usuario_id} como firmante (orden={orden}) "
            f"del documento id={documento_firma_id} (firmante id={firmante.pk}).",
            objeto=firmante,
        )
        NotificacionService.crear(
            usuario_destino_id=usuario_id,
            mensaje=(
                f"Se le asignó como firmante (orden={orden}) del documento "
                f"'{firmante.documento_firma.tipo_documento.nombre_documento}'. "
                f"Queda pendiente su firma."
            ),
            tipo='alerta',
            notificar_email=True,
        )
        return firmante

    @staticmethod
    @transaction.atomic
    def asignar_firmantes(documento_firma_id, usuarios_ids_en_orden, ejecutor):
        """Crea todos los firmantes de un documento respetando el orden de la lista."""
        firmantes = []
        for i, usuario_id in enumerate(usuarios_ids_en_orden, start=1):
            firmantes.append(
                DocumentoFirmanteService.asignar_firmante(
                    documento_firma_id, usuario_id, i, ejecutor
                )
            )
        return firmantes

    @staticmethod
    @transaction.atomic
    def generar_codigo_verificacion(documento_firmante_id, ejecutor):
        firmante = DocumentoFirmanteSelector.obtener(documento_firmante_id)
        codigo = f"{secrets.randbelow(1000000):06d}"
        firmante.codigo_verificacion = codigo
        firmante.save(update_fields=['codigo_verificacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se generó un código de verificación para el firmante "
            f"'{firmante.usuario.username}' (firmante id={firmante.pk}).",
            objeto=firmante,
        )
        NotificacionService.crear(
            usuario_destino_id=firmante.usuario_id,
            mensaje=(
                f"Su código de verificación para firmar el documento "
                f"'{firmante.documento_firma.tipo_documento.nombre_documento}' es: {codigo}"
            ),
            tipo='info',
            notificar_email=True,
        )
        return firmante

    @staticmethod
    @transaction.atomic
    def firmar(documento_firmante_id, codigo_verificacion, ip_firma, ruta_firma, ejecutor):
        firmante = DocumentoFirmanteSelector.obtener(documento_firmante_id)
        DocumentoFirmanteValidator.validar_firma(firmante, codigo_verificacion, ejecutor)
        from django.utils import timezone
        firmante.estado = 'FIRMADO'
        firmante.ip_firma = ip_firma
        firmante.ruta_firma = ruta_firma
        firmante.fecha_firma = timezone.now()
        firmante.save(update_fields=['estado', 'ip_firma', 'ruta_firma', 'fecha_firma'])
        HistorialService.registrar(
            ejecutor,
            f"'{firmante.usuario.username}' firmó el documento "
            f"'{firmante.documento_firma.tipo_documento.nombre_documento}' "
            f"versión {firmante.documento_firma.version} (firmante id={firmante.pk}).",
            objeto=firmante,
        )
        if DocumentoFirmanteSelector.todos_firmaron(firmante.documento_firma_id):
            DocumentoFirmaService.marcar_firmado_completamente(firmante.documento_firma_id, ejecutor)
        return firmante

    @staticmethod
    @transaction.atomic
    def rechazar(documento_firmante_id, motivo_rechazo, ejecutor):
        firmante = DocumentoFirmanteSelector.obtener(documento_firmante_id)
        DocumentoFirmanteValidator.validar_rechazo(motivo_rechazo, firmante, ejecutor)
        firmante.estado = 'RECHAZADO'
        firmante.motivo_rechazo = motivo_rechazo
        firmante.save(update_fields=['estado', 'motivo_rechazo'])
        HistorialService.registrar(
            ejecutor,
            f"'{firmante.usuario.username}' rechazó firmar el documento "
            f"'{firmante.documento_firma.tipo_documento.nombre_documento}' "
            f"versión {firmante.documento_firma.version}. Motivo: {motivo_rechazo} "
            f"(firmante id={firmante.pk}).",
            objeto=firmante,
        )
        DocumentoFirmaService.marcar_rechazado(firmante.documento_firma_id, ejecutor)
        return firmante

    @staticmethod
    def listar_por_documento(documento_firma_id):
        return DocumentoFirmanteSelector.listar_por_documento(documento_firma_id)

    @staticmethod
    def listar_pendientes_por_usuario(usuario_id):
        return DocumentoFirmanteSelector.listar_pendientes_por_usuario(usuario_id)

    @staticmethod
    def obtener_siguiente_turno(documento_firma_id):
        return DocumentoFirmanteSelector.obtener_siguiente_turno(documento_firma_id)

    @staticmethod
    @transaction.atomic
    def eliminar(documento_firmante_id, ejecutor):
        firmante = DocumentoFirmanteSelector.obtener(documento_firmante_id)
        DocumentoFirmanteValidator.validar_eliminacion(firmante)
        descripcion = (
            f"Se eliminó al firmante '{firmante.usuario.username}' "
            f"del documento id={firmante.documento_firma_id} (firmante id={firmante.pk})."
        )
        HistorialService.registrar(ejecutor, descripcion)
        firmante.delete()
        return True