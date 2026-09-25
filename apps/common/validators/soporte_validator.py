from rest_framework.exceptions import ValidationError

class SoporteValidator:
    """
    Réplica de las validaciones @Valid del MailSoporteDTO original
    (asunto/mensaje obligatorios, sin más reglas de negocio en Thymeleaf).
    """
    @staticmethod
    def validar_solicitud(asunto, mensaje):
        errores = {}
        if not asunto or not asunto.strip():
            errores["asunto"] = "El asunto es obligatorio."
        if not mensaje or not mensaje.strip():
            errores["mensaje"] = "El mensaje es obligatorio."
        if errores:
            raise ValidationError(errores)