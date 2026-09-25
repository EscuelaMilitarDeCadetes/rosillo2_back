from django.db import transaction
from apps.common.models import Aprobacion
from apps.common.selectors.aprobacion_selector import AprobacionSelector
from apps.common.validators.aprobacion_validator import AprobacionValidator
from apps.common.services.historial_service import HistorialService
from apps.common.services.notificacion_service import NotificacionService


class AprobacionService:
    @staticmethod
    def listar():
        return AprobacionSelector.listar()

    @staticmethod
    def obtener(aprobacion_id):
        return AprobacionSelector.obtener(aprobacion_id)

    @staticmethod
    @transaction.atomic
    def crear(usuario_revisor_id, tipo_documento_id, id_documento, ejecutor, estado='PENDIENTE', observacion=None):
        AprobacionValidator.validar_creacion(usuario_revisor_id, tipo_documento_id, id_documento, estado)
        aprobacion = Aprobacion.objects.create(
            usuario_revisor_id=usuario_revisor_id,
            tipo_documento_id=tipo_documento_id,
            id_documento=id_documento,
            estado=estado,
            observacion=observacion,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó una solicitud de aprobación (tipo_documento_id={tipo_documento_id}, "
            f"id_documento={id_documento}, revisor_id={usuario_revisor_id}, id={aprobacion.pk}).",
            objeto=aprobacion,
        )
        if estado == 'PENDIENTE':
            NotificacionService.crear(
                usuario_destino_id=usuario_revisor_id,
                mensaje=(
                    f"Tiene una nueva solicitud de aprobación pendiente "
                    f"(id={aprobacion.pk})."
                ),
                tipo='alerta',
                notificar_email=True,
            )
        return aprobacion

    @staticmethod
    @transaction.atomic
    def aprobar(aprobacion_id, ejecutor, observacion=None):
        aprobacion = AprobacionSelector.obtener(aprobacion_id)
        AprobacionValidator.validar_cambio_estado(aprobacion, "APROBADO")
        aprobacion.estado = 'APROBADO'
        if observacion is not None:
            aprobacion.observacion = observacion
        aprobacion.save(update_fields=['estado', 'observacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se aprobó el documento tipo_documento_id={aprobacion.tipo_documento_id}, "
            f"id_documento={aprobacion.id_documento} (aprobacion id={aprobacion.pk}).",
            objeto=aprobacion,
        )
        return aprobacion

    @staticmethod
    @transaction.atomic
    def rechazar(aprobacion_id, ejecutor, observacion):
        AprobacionValidator.validar_rechazo(observacion)
        aprobacion = AprobacionSelector.obtener(aprobacion_id)
        AprobacionValidator.validar_cambio_estado(aprobacion, "RECHAZADO")
        aprobacion.estado = 'RECHAZADO'
        aprobacion.observacion = observacion
        aprobacion.save(update_fields=['estado', 'observacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se rechazó el documento tipo_documento_id={aprobacion.tipo_documento_id}, "
            f"id_documento={aprobacion.id_documento} (aprobacion id={aprobacion.pk}). "
            f"Motivo: {observacion}",
            objeto=aprobacion,
        )
        return aprobacion

    @staticmethod
    def listar_pendientes(usuario_revisor_id=None):
        return AprobacionSelector.listar_pendientes(usuario_revisor_id)

    @staticmethod
    def listar_por_documento(tipo_documento_id, id_documento):
        return AprobacionSelector.listar_por_documento(tipo_documento_id, id_documento)

    @staticmethod
    def obtener_ultima_por_documento(tipo_documento_id, id_documento):
        return AprobacionSelector.obtener_ultima_por_documento(tipo_documento_id, id_documento)