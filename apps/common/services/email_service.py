# apps/common/services/email_service.py
"""
Servicio central de envío de correo — análogo a HistorialService.

Cualquier service de cualquier módulo debe pasar por aquí en vez de
llamar a send_mail() o a la tarea de Celery directamente, para que:
  1. Haya un solo punto de entrada, fácil de testear/mockear.
  2. El envío siempre quede diferido a transaction.on_commit(), sin que
     cada caller tenga que acordarse de hacerlo (evita el bug de enviar
     un correo cuya transacción termina en rollback).

Modos de envío (settings.EMAIL_MODO_ENVIO, se controla desde el .env):
  - 'celery'  -> encola en Celery (requiere Redis + worker corriendo).
                 Es el comportamiento original.
  - 'hilo'    -> envía en un hilo aparte del mismo proceso web. NO necesita
                 Redis ni worker: sirve para ambientes donde sólo se puede
                 tener UN proceso/consola corriendo. La petición HTTP no
                 espera a que el correo salga.
  - 'sincrono'-> envía dentro de la misma petición (la respuesta tarda lo
                 que tarde el servidor SMTP). Útil para depurar.

Redirección para pruebas (settings.EMAIL_REDIRIGIR_A):
  Si tiene un valor, TODOS los correos se envían a esa(s) dirección(es) en
  lugar de a los destinatarios reales, y en el asunto/cuerpo se indica a
  quién iban dirigidos. Permite probar flujos completos aunque los correos
  institucionales de los usuarios aún no existan. En producción se fuerza
  a vacío (ver config/settings/production.py).
"""
import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from apps.common.tasks import enviar_email_task

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def enviar(subject, message, recipient_list, html_message=None, from_email=None):
        """
        Programa el envío del correo para cuando la transacción actual (si
        la hay) haga commit; si no hay transacción activa, se despacha de
        inmediato (comportamiento estándar de transaction.on_commit).
        Nunca propaga errores de envío al caller.
        """
        destinatarios = [d.strip() for d in (recipient_list or []) if d and d.strip()]
        subject, message, html_message, destinatarios = EmailService._aplicar_redireccion(
            subject, message, html_message, destinatarios
        )
        if not destinatarios:
            logger.warning(f"[Email] Correo '{subject}' descartado: no hay destinatarios con email.")
            return

        payload = dict(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            html_message=html_message,
        )
        transaction.on_commit(lambda: EmailService._despachar(payload))

    # ------------------------------------------------------------------ #

    @staticmethod
    def _despachar(payload):
        modo = getattr(settings, 'EMAIL_MODO_ENVIO', 'celery')
        try:
            if modo == 'hilo':
                threading.Thread(
                    target=EmailService._enviar_ahora, kwargs=payload, daemon=True
                ).start()
            elif modo == 'sincrono':
                EmailService._enviar_ahora(**payload)
            else:
                enviar_email_task.delay(**payload)
        except Exception:
            # Ej.: modo 'celery' sin Redis disponible. El dato de negocio ya
            # quedó guardado (estamos en on_commit); no se debe responder 500.
            logger.exception(
                f"[Email] No se pudo despachar el correo a {payload['recipient_list']} (modo={modo})."
            )

    @staticmethod
    def _enviar_ahora(subject, message, from_email, recipient_list, html_message=None):
        intentos = 2
        for intento in range(1, intentos + 1):
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    html_message=html_message,
                )
                logger.info(f"[Email] Enviado '{subject}' a {recipient_list}.")
                return True
            except Exception:
                logger.exception(
                    f"[Email] Fallo al enviar '{subject}' a {recipient_list} "
                    f"(intento {intento}/{intentos})."
                )
        return False

    @staticmethod
    def _aplicar_redireccion(subject, message, html_message, destinatarios):
        redirigir_a = [
            d.strip() for d in str(getattr(settings, 'EMAIL_REDIRIGIR_A', '') or '').split(',')
            if d.strip()
        ]
        if not redirigir_a:
            return subject, message, html_message, destinatarios

        originales = ', '.join(destinatarios) or '(usuario sin email registrado)'
        aviso = f"[PRUEBAS] Este correo iba dirigido a: {originales}"
        subject = f"[PRUEBAS -> {originales}] {subject}"
        message = f"{aviso}\n\n{message or ''}"
        if html_message:
            html_message = f"<p><strong>{aviso}</strong></p><hr>{html_message}"
        return subject, message, html_message, redirigir_a
