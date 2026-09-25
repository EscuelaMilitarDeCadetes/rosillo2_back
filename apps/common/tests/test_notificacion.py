from django.test import TestCase
from django.core import mail
from rest_framework.exceptions import ValidationError
from .base import CommonFixturesMixin
from apps.common.services.notificacion_service import NotificacionService
from apps.common.services.tarea_service import TareaService


class NotificacionServiceTests(CommonFixturesMixin, TestCase):

    def test_crear_notificacion_exitoso(self):
        notificacion = NotificacionService.crear(
            usuario_destino_id=self.otro_usuario.pk,
            mensaje='Tiene una tarea pendiente.',
            tipo='alerta',
        )
        self.assertFalse(notificacion.leido)

    def test_crear_notificacion_sin_usuario_destino_falla(self):
        with self.assertRaises(ValidationError):
            NotificacionService.crear(usuario_destino_id=None, mensaje='Mensaje')

    def test_crear_notificacion_mensaje_vacio_falla(self):
        with self.assertRaises(ValidationError):
            NotificacionService.crear(usuario_destino_id=self.otro_usuario.pk, mensaje='   ')

    def test_crear_notificacion_tipo_invalido_falla(self):
        with self.assertRaises(ValidationError):
            NotificacionService.crear(
                usuario_destino_id=self.otro_usuario.pk, mensaje='Mensaje', tipo='urgente'
            )

    def test_crear_notificacion_con_email_envia_correo(self):
        with self.captureOnCommitCallbacks(execute=True):
            NotificacionService.crear(
                usuario_destino_id=self.otro_usuario.pk,
                mensaje='Recordatorio de entrega de documento.',
                tipo='alerta',
                notificar_email=True,
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.otro_usuario.email])

    def test_marcar_leida(self):
        notificacion = NotificacionService.crear(
            usuario_destino_id=self.otro_usuario.pk, mensaje='Mensaje'
        )
        leida = NotificacionService.marcar_leida(notificacion.pk)
        self.assertTrue(leida.leido)

    def test_marcar_todas_leidas(self):
        NotificacionService.crear(usuario_destino_id=self.otro_usuario.pk, mensaje='Mensaje 1')
        NotificacionService.crear(usuario_destino_id=self.otro_usuario.pk, mensaje='Mensaje 2')
        actualizadas = NotificacionService.marcar_todas_leidas(self.otro_usuario.pk)
        self.assertEqual(actualizadas, 2)

    def test_listar_por_usuario_solo_no_leidas(self):
        n1 = NotificacionService.crear(usuario_destino_id=self.otro_usuario.pk, mensaje='Mensaje 1')
        NotificacionService.crear(usuario_destino_id=self.otro_usuario.pk, mensaje='Mensaje 2')
        NotificacionService.marcar_leida(n1.pk)
        resultados = NotificacionService.listar_por_usuario(self.otro_usuario.pk, solo_no_leidas=True)
        self.assertEqual(resultados.count(), 1)

    # --- Job de recordatorios ---

    def test_enviar_recordatorios_tareas_vencida_genera_notificacion(self):
        from django.utils import timezone
        from datetime import timedelta
        tarea = TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Entregar informe de avance',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() - timedelta(days=2)).date(),
        )
        creadas = NotificacionService.enviar_recordatorios_tareas()
        self.assertEqual(len(creadas), 1)
        self.assertIn('venció', creadas[0].mensaje)

    def test_enviar_recordatorios_tareas_proxima_a_vencer_genera_notificacion(self):
        from django.utils import timezone
        from datetime import timedelta
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Entregar informe de avance',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() + timedelta(days=1)).date(),
        )
        creadas = NotificacionService.enviar_recordatorios_tareas(dias_anticipacion=3)
        self.assertEqual(len(creadas), 1)
        self.assertIn('debe cumplirse', creadas[0].mensaje)

    def test_enviar_recordatorios_no_duplica_el_mismo_dia(self):
        from django.utils import timezone
        from datetime import timedelta
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Entregar informe de avance',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() - timedelta(days=1)).date(),
        )
        primera_corrida = NotificacionService.enviar_recordatorios_tareas()
        segunda_corrida = NotificacionService.enviar_recordatorios_tareas()
        self.assertEqual(len(primera_corrida), 1)
        self.assertEqual(len(segunda_corrida), 0)

    def test_enviar_recordatorios_tarea_completada_no_genera_aviso(self):
        from django.utils import timezone
        from datetime import timedelta
        tarea = TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Entregar informe de avance',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() - timedelta(days=1)).date(),
        )
        TareaService.completar(tarea.pk, ejecutor=self.otro_usuario)
        creadas = NotificacionService.enviar_recordatorios_tareas()
        self.assertEqual(len(creadas), 0)