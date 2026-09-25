# apps/common/services/email_service.py
"""
Servicio central de envío de correo — análogo a HistorialService.

Cualquier service de cualquier módulo debe pasar por aquí en vez de
llamar a send_mail() o a la tarea de Celery directamente, para que:
  1. Haya un solo punto de entrada, fácil de testear/mockear.
  2. El envío siempre quede diferido a transaction.on_commit(), sin que
     cada caller tenga que acordarse de hacerlo (evita el bug de enviar
     un correo cuya transacción termina en rollback).
"""
from django.conf import settings
from django.db import transaction

from apps.common.tasks import enviar_email_task


class EmailService:

    @staticmethod
    def enviar(subject, message, recipient_list, html_message=None, from_email=None):
        """
        Encola el envío del correo vía Celery. No lo envía en este hilo.
        Se difiere automáticamente hasta que la transacción actual (si la
        hay) haga commit; si no hay una transacción activa, se encola de
        inmediato (comportamiento estándar de transaction.on_commit).
        """
        payload = dict(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
        )
        transaction.on_commit(lambda: enviar_email_task.delay(**payload))