#apps/common/services/notificacion_service.py
from django.db import transaction
from apps.common.services.email_service import EmailService
from apps.common.models import Notificacion
from apps.common.selectors.notificacion_selector import NotificacionSelector
from apps.common.selectors.tarea_selector import TareaSelector
from apps.common.validators.notificacion_validator import NotificacionValidator
from apps.common.services.historial_service import HistorialService

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class NotificacionService:
    @staticmethod
    def listar():
        return NotificacionSelector.listar()

    @staticmethod
    def obtener(notificacion_id):
        return NotificacionSelector.obtener(notificacion_id)

    @staticmethod
    @transaction.atomic
    def crear(usuario_destino_id, mensaje, tipo=None, url_relacionada=None, notificar_email=False):
        NotificacionValidator.validar_creacion(usuario_destino_id, mensaje, tipo, url_relacionada)

        notificacion = Notificacion.objects.create(
            usuario_destino_id=usuario_destino_id,
            mensaje=mensaje,
            tipo=tipo,
            url_relacionada=url_relacionada,
        )

        if notificar_email:
            NotificacionService._enviar_email(notificacion)

        # --- empujar en vivo por WebSocket ---
        channel_layer = get_channel_layer()
        transaction.on_commit(lambda: async_to_sync(channel_layer.group_send)(
            f"notificaciones_{usuario_destino_id}",
            {
                "type": "notificacion_nueva",
                "data": {
                    "id": notificacion.pk,
                    "mensaje": notificacion.mensaje,
                    "tipo": notificacion.tipo,
                    "url_relacionada": notificacion.url_relacionada,
                    "fecha_creacion": notificacion.fecha_creacion.isoformat(),
                },
            },
        ))
        return notificacion

    @staticmethod
    def _enviar_email(notificacion):
        titulos_por_tipo = {
            'alerta': 'Alerta - Rosillo',
            'error': 'Error - Rosillo',
            'exito': 'Confirmación - Rosillo',
            'info': 'Notificación - Rosillo',
        }
        asunto = titulos_por_tipo.get(notificacion.tipo, "Notificación ESMIC - ROSILLO")
        contenido_html = (
            "<p>Gusto en saludarlo Señor(a),</p>"
            f"<p>{notificacion.mensaje}</p>"
            "<p>No responder a este mensaje.</p>"
        )
        EmailService.enviar(
            subject=asunto,
            message=notificacion.mensaje,
            recipient_list=[notificacion.usuario_destino.email],
            html_message=contenido_html,
        )

    @staticmethod
    @transaction.atomic
    def marcar_leida(notificacion_id):
        notificacion = NotificacionSelector.obtener(notificacion_id)
        notificacion.leido = True
        notificacion.save(update_fields=['leido'])
        return notificacion

    @staticmethod
    @transaction.atomic
    def marcar_todas_leidas(usuario_id):
        return Notificacion.objects.filter(usuario_destino_id=usuario_id, leido=False).update(leido=True)

    @staticmethod
    @transaction.atomic
    def eliminar(notificacion_id, ejecutor):
        notificacion = NotificacionSelector.obtener(notificacion_id)
        NotificacionValidator.validar_eliminacion(notificacion)
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó la notificación id={notificacion.pk} "
            f"del usuario '{notificacion.usuario_destino.username}'.",
        )
        notificacion.delete()
        return True

    @staticmethod
    def listar_por_usuario(usuario_id, solo_no_leidas=False):
        return NotificacionSelector.listar_por_usuario(usuario_id, solo_no_leidas=solo_no_leidas)

    # --- Job periódico de recordatorios (Celery beat / cron) ---

    @staticmethod
    @transaction.atomic
    def enviar_recordatorios_tareas(dias_anticipacion=3):
        """
        Recorre las tareas vencidas y las próximas a vencer, y genera una
        Notificacion (con email) por cada una, evitando duplicar el aviso
        el mismo día para la misma tarea. Pensado para ejecutarse desde un
        cron/Celery beat diario, no desde una vista.
        """
        creadas = []

        for tarea in TareaSelector.listar_vencidas():
            creadas.append(NotificacionService._notificar_tarea(tarea, vencida=True))

        for tarea in TareaSelector.listar_proximas_a_vencer(dias=dias_anticipacion):
            creadas.append(NotificacionService._notificar_tarea(tarea, vencida=False))

        creadas = [n for n in creadas if n is not None]

        if creadas:
            HistorialService.registrar(
                None,
                f"[SISTEMA] Job de recordatorios: se generaron {len(creadas)} "
                f"notificaciones de tareas próximas a vencer o vencidas.",
            )
        return creadas

    @staticmethod
    def _notificar_tarea(tarea, vencida):
        url = f"/tareas/{tarea.pk}"
        if NotificacionSelector.existe_recordatorio_hoy(tarea.asignado_a_id, url, tipo='alerta'):
            return None

        if vencida:
            mensaje = (
                f"La tarea '{tarea.descripcion}' venció el {tarea.fecha_limite} "
                f"y aún no ha sido completada."
            )
        else:
            mensaje = (
                f"La tarea '{tarea.descripcion}' debe cumplirse antes del "
                f"{tarea.fecha_limite}."
            )

        return NotificacionService.crear(
            usuario_destino_id=tarea.asignado_a_id,
            mensaje=mensaje,
            tipo='alerta',
            url_relacionada=url,
            notificar_email=True,
        )