# apps/common/services/soporte_service.py
"""
Réplica de SolicitudSoporteController.solicitudSoporte() /
MailSenderConfig.sendSupportEmail() del Thymeleaf original.

Diferencia deliberada respecto al original: el Java original hacía
helper.setFrom(recipientEmail, recipientEmail), es decir, enviaba el correo
"como si fuera" el usuario. Eso rompe SPF/DKIM en la mayoría de relays SMTP
reales y termina en spam o rebote. Aquí se envía desde
settings.DEFAULT_FROM_EMAIL (remitente autorizado) y el email del usuario
se incluye en el cuerpo del mensaje, igual que hacía el 'content' original.
Si se requiere réplica exacta del comportamiento, avísame y lo ajusto.
"""
from django.conf import settings
from apps.common.validators.soporte_validator import SoporteValidator
from apps.common.services.email_service import EmailService
from apps.common.services.historial_service import HistorialService


class SoporteService:
    @staticmethod
    def enviar_solicitud(usuario, asunto, mensaje):
        SoporteValidator.validar_solicitud(asunto, mensaje)

        html_message = (
            f"<p>Soy el usuario \"{usuario.username}\" (usuario id={usuario.pk})</p>"
            f"<p>y envío este correo para solicitar una solución con \"{asunto}\"</p>"
            f"<p>el cual es una PQRS con el siguiente mensaje</p>"
            f"<p>\"{mensaje}\"</p>"
        )

        EmailService.enviar(
            subject=f"{settings.PQRS_SUBJECT_PREFIX} - {asunto}",
            message=mensaje,  # fallback texto plano
            recipient_list=[settings.EMAIL_SOPORTE],
            html_message=html_message,
        )

        HistorialService.registrar(usuario, "Se envía una solicitud de soporte")