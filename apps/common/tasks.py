# apps/common/tasks.py
import logging

from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email_task(self, subject, message, from_email, recipient_list, html_message=None):
    """
    Tarea real de envío. No se llama directamente desde ningún service:
    todo pasa por EmailService.enviar(), que la encola.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
        )
    except Exception as exc:
        logger.exception(
            f"Fallo al enviar email a {recipient_list} "
            f"(intento {self.request.retries + 1}/{self.max_retries + 1})"
        )
        raise self.retry(exc=exc)


@shared_task
def enviar_recordatorios_tareas_task(dias_anticipacion=3):
    """
    Tarea periódica (ver CELERY_BEAT_SCHEDULE). Reemplaza la ejecución
    manual vía cron externo que estaba pendiente — cierra el diseño que
    ya anticipaba NotificacionService.enviar_recordatorios_tareas().
    El endpoint administrativo que la dispara manualmente se mantiene
    intacto para corridas puntuales; esta tarea es la corrida automática
    diaria.
    """
    from apps.common.services.notificacion_service import NotificacionService

    creadas = NotificacionService.enviar_recordatorios_tareas(dias_anticipacion=dias_anticipacion)
    logger.info(f"[Celery beat] enviar_recordatorios_tareas_task: {len(creadas)} notificaciones generadas.")
    return len(creadas)

@shared_task
def verificar_integridad_documentos_task():
    """
    Tarea periódica (ver CELERY_BEAT_SCHEDULE). Recalcula el hash de cada
    DocumentoFirma y lo compara contra el registrado al crearlo; genera
    Notificacion + Historial si detecta discrepancia o archivo faltante.
    """
    from apps.common.services.documento_firma_service import DocumentoFirmaService
    resultados = DocumentoFirmaService.verificar_integridad_todos()
    logger.info(
        f"[Celery beat] verificar_integridad_documentos_task: "
        f"{resultados['verificados']} verificados, {resultados['alterados']} con alerta."
    )
    return resultados