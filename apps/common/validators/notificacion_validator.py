from rest_framework.exceptions import ValidationError
from apps.common.models import Notificacion

TIPOS_VALIDOS = {choice[0] for choice in Notificacion.TIPO_CHOICES}


class NotificacionValidator:
    @staticmethod
    def validar_creacion(usuario_destino_id, mensaje, tipo=None, url_relacionada=None):
        NotificacionValidator._validar_usuario_destino(usuario_destino_id)
        NotificacionValidator._validar_mensaje(mensaje)
        NotificacionValidator._validar_tipo(tipo)
        NotificacionValidator._validar_url(url_relacionada)

    @staticmethod
    def _validar_usuario_destino(usuario_destino_id):
        if not usuario_destino_id:
            raise ValidationError({"usuario_destino": "El usuario destinatario es obligatorio."})

    @staticmethod
    def _validar_mensaje(mensaje):
        if not mensaje or not mensaje.strip():
            raise ValidationError({"mensaje": "El mensaje de la notificación es obligatorio."})

    @staticmethod
    def _validar_tipo(tipo):
        if tipo is not None and tipo not in TIPOS_VALIDOS:
            raise ValidationError(
                {"tipo": f"'{tipo}' no es un tipo válido. Use uno de: {sorted(TIPOS_VALIDOS)}."}
            )

    @staticmethod
    def _validar_url(url_relacionada):
        if url_relacionada is not None and len(url_relacionada) > 255:
            raise ValidationError(
                {"url_relacionada": "La URL relacionada supera el máximo de 255 caracteres."}
            )