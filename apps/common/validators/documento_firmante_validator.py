from rest_framework.exceptions import ValidationError
from apps.common.selectors.documento_firma_selector import DocumentoFirmaSelector
from apps.common.selectors.documento_firmante_selector import DocumentoFirmanteSelector


class DocumentoFirmanteValidator:
    @staticmethod
    def validar_creacion(documento_firma_id, usuario_id, orden):
        DocumentoFirmanteValidator._validar_documento_firma(documento_firma_id)
        DocumentoFirmanteValidator._validar_usuario(usuario_id)
        DocumentoFirmanteValidator._validar_orden(orden)
        DocumentoFirmanteValidator._validar_unicidad(documento_firma_id, usuario_id)

    @staticmethod
    def validar_firma(documento_firmante, codigo_verificacion_ingresado, ejecutor):
        if ejecutor is None or ejecutor.pk != documento_firmante.usuario_id:
            raise ValidationError("Solo el firmante asignado puede registrar esta firma.")
        if documento_firmante.estado == 'FIRMADO':
            raise ValidationError("Este firmante ya registró su firma.")
        if documento_firmante.estado == 'RECHAZADO':
            raise ValidationError("Este firmante ya rechazó firmar el documento.")
        if not codigo_verificacion_ingresado:
            raise ValidationError({"codigo_verificacion": "Debe ingresar el código de verificación enviado."})
        if documento_firmante.codigo_verificacion != codigo_verificacion_ingresado:
            raise ValidationError({"codigo_verificacion": "El código de verificación no es correcto."})
        siguiente = DocumentoFirmanteSelector.obtener_siguiente_turno(documento_firmante.documento_firma_id)
        if siguiente is None:
            raise ValidationError("No existen firmas pendientes.")
        if siguiente.pk != documento_firmante.pk:
            raise ValidationError("Aún no corresponde el turno de firma.")

    @staticmethod
    def validar_rechazo(motivo_rechazo, documento_firmante, ejecutor):
        if ejecutor is None or ejecutor.pk != documento_firmante.usuario_id:
            raise ValidationError("Solo el firmante asignado puede rechazar esta firma.")
        if not motivo_rechazo or not motivo_rechazo.strip():
            raise ValidationError({"motivo_rechazo": "Debe indicar el motivo del rechazo de la firma."})

    @staticmethod
    def validar_eliminacion(documento_firmante):
        if documento_firmante.estado == 'FIRMADO':
            raise ValidationError("No se puede eliminar un firmante que ya registró su firma.")

    @staticmethod
    def _validar_documento_firma(documento_firma_id):
        if not documento_firma_id:
            raise ValidationError({"documento_firma": "El documento a firmar es obligatorio."})
        if not DocumentoFirmaSelector.buscar(documento_firma_id):
            raise ValidationError(
                {"documento_firma": f"No existe un DocumentoFirma con id={documento_firma_id}."}
            )

    @staticmethod
    def _validar_usuario(usuario_id):
        if not usuario_id:
            raise ValidationError({"usuario": "El usuario firmante es obligatorio."})

    @staticmethod
    def _validar_orden(orden):
        if orden is None or orden < 1:
            raise ValidationError({"orden": "El orden de firma debe ser un entero mayor o igual a 1."})

    @staticmethod
    def _validar_unicidad(documento_firma_id, usuario_id, excluir_id=None):
        if DocumentoFirmanteSelector.existe_firmante(documento_firma_id, usuario_id, excluir_id=excluir_id):
            raise ValidationError("Este usuario ya está registrado como firmante de este documento.")