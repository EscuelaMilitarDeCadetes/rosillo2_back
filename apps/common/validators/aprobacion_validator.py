from rest_framework.exceptions import ValidationError
from apps.common.models import Aprobacion
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector
from apps.common.selectors.aprobacion_selector import AprobacionSelector

ESTADOS_VALIDOS = {choice[0] for choice in Aprobacion.ESTADO_CHOICES}

class AprobacionValidator:
    @staticmethod
    def validar_creacion(usuario_revisor_id, tipo_documento_id, id_documento, estado):
        AprobacionValidator._validar_usuario_revisor(usuario_revisor_id)
        AprobacionValidator._validar_tipo_documento(tipo_documento_id)
        AprobacionValidator._validar_id_documento(id_documento)
        AprobacionValidator._validar_estado(estado)
        AprobacionValidator._validar_unicidad(usuario_revisor_id, tipo_documento_id, id_documento)

    @staticmethod
    def _validar_usuario_revisor(usuario_revisor_id):
        if not usuario_revisor_id:
            raise ValidationError({"usuario_revisor": "El usuario revisor es obligatorio."})

    @staticmethod
    def _validar_tipo_documento(tipo_documento_id):
        if not tipo_documento_id:
            raise ValidationError({"tipo_documento": "El tipo de documento es obligatorio."})
        if not TipoDocumentoSelector.buscar(tipo_documento_id):
            raise ValidationError({"tipo_documento": f"No existe un TipoDocumento con id={tipo_documento_id}."})

    @staticmethod
    def _validar_id_documento(id_documento):
        if id_documento is None:
            raise ValidationError({"id_documento": "El id del documento a revisar es obligatorio."})

    @staticmethod
    def _validar_estado(estado):
        if not estado or estado not in ESTADOS_VALIDOS:
            raise ValidationError(
                {"estado": f"El estado debe ser uno de: {sorted(ESTADOS_VALIDOS)}."}
            )

    @staticmethod
    def _validar_unicidad(usuario_revisor_id, tipo_documento_id, id_documento, excluir_id=None):
        if AprobacionSelector.existe_aprobacion(
            usuario_revisor_id, tipo_documento_id, id_documento, excluir_id=excluir_id
        ):
            raise ValidationError(
                "Ya existe un registro de aprobación de este revisor para este documento."
            )
    
    @staticmethod
    def validar_cambio_estado(aprobacion, nuevo_estado):
        if aprobacion.estado != "PENDIENTE":
            raise ValidationError(
                "Esta aprobación ya fue resuelta y no puede cambiar nuevamente de estado."
            )
        if nuevo_estado not in ("APROBADO", "RECHAZADO"):
            raise ValidationError(
                "Estado de aprobación inválido."
            )
    
    @staticmethod
    def validar_rechazo(observacion):
        if not observacion or not observacion.strip():
            raise ValidationError({
                "observacion": "Debe indicar el motivo del rechazo."
            })