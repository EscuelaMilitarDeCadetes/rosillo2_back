"""
Pruebas de las operaciones de ciclo de vida de Usuario que la Regla RN-06
centraliza en este módulo: crear_credenciales, activar_usuario,
desactivar_usuario, reactivar_usuario y reasignar_persona_a_usuario
(implementación concreta de GestionUsuarioInterface).

A diferencia de test_permisos.py / test_flujos_creacion.py /
test_reemplazo_retiro.py (que sí usan APIClient porque necesitan
verificar permission_classes de DRF), estas pruebas llaman a
VinculacionService directamente, sin HTTP, conforme al estándar de
11_backend_logic.md ("los tests viven a nivel de service"): ninguno de
estos métodos tiene lógica de permisos que solo pueda verificarse pasando
por la capa HTTP.
"""
#apps/integracion/tests/test_ciclo_vida_usuario.py
from unittest.mock import patch

from django.http import Http404
from django.test import TestCase

from apps.common.models.historial import Historial
from apps.institucional.models.persona import Persona
from apps.usuarios.models import UsuarioXPersona

from apps.integracion.services.vinculacion_service import VinculacionService
from .base import IntegracionFixturesMixin


class CicloVidaUsuarioTests(IntegracionFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        # persona/usuario/asignacion son propios de este archivo: ningún
        # otro test de integracion los necesita, por eso no se agregan
        # al mixin compartido (evita inflar el fixture de las demás clases).
        self.persona = Persona.objects.create(
            grado=self.grado, nombre='Persona', apellido='Prueba',
            documento='CV-1', celular='3000000001', correo='ciclo.vida@esmic.edu.co',
        )
        self.usuario = VinculacionService.crear_credenciales(
            data={
                'username': 'ciclo.vida@esmic.edu.co',
                'email': 'ciclo.vida@esmic.edu.co',
                'password': 'Temporal123*',
                'persona_fk': self.persona.pk,
            },
            ejecutor=self.ejecutor,
        )
        self.asignacion = UsuarioXPersona.objects.get(usuario=self.usuario, estado=True)

    # ---------------- crear_credenciales ----------------

    def test_crear_credenciales_crea_usuario_y_asigna_persona(self):
        persona2 = Persona.objects.create(
            grado=self.grado, nombre='Otra', apellido='Persona',
            documento='CV-2', celular='3000000002', correo='otra.cv@esmic.edu.co',
        )
        usuario = VinculacionService.crear_credenciales(
            data={
                'username': 'otra.cv@esmic.edu.co',
                'email': 'otra.cv@esmic.edu.co',
                'password': 'Password123*',
                'persona_fk': persona2.pk,
            },
            ejecutor=self.ejecutor,
        )
        self.assertIsNotNone(usuario.id)
        self.assertTrue(usuario.check_password('Password123*'))
        self.assertTrue(usuario.debe_cambiar_password)
        asignacion = UsuarioXPersona.objects.get(usuario=usuario)
        self.assertEqual(asignacion.persona_id, persona2.pk)
        self.assertTrue(asignacion.estado)
        self.assertTrue(
            Historial.objects.filter(
                usuario=self.ejecutor, accion__icontains="credenciales"
            ).exists()
        )

    def test_crear_credenciales_sin_persona_no_crea_asignacion(self):
        usuario = VinculacionService.crear_credenciales(
            data={
                'username': 'sinpersona.cv@esmic.edu.co',
                'email': 'sinpersona.cv@esmic.edu.co',
                'password': 'Password123*',
            },
            ejecutor=self.ejecutor,
        )
        self.assertIsNotNone(usuario.id)
        self.assertFalse(UsuarioXPersona.objects.filter(usuario=usuario).exists())

    def test_crear_credenciales_con_persona_inexistente_no_falla(self):
        usuario = VinculacionService.crear_credenciales(
            data={
                'username': 'personafalsa.cv@esmic.edu.co',
                'email': 'personafalsa.cv@esmic.edu.co',
                'password': 'Password123*',
                'persona_fk': 999999,
            },
            ejecutor=self.ejecutor,
        )
        self.assertIsNotNone(usuario.id)
        self.assertFalse(UsuarioXPersona.objects.filter(usuario=usuario).exists())

    @patch("django.db.transaction.on_commit")
    def test_crear_credenciales_programa_envio_de_enlace(self, mock_on_commit):
        VinculacionService.crear_credenciales(
            data={
                'username': 'correo.cv@esmic.edu.co',
                'email': 'correo.cv@esmic.edu.co',
                'password': 'Password123*',
            },
            ejecutor=self.ejecutor,
        )
        mock_on_commit.assert_called_once()

    @patch("apps.common.tasks.send_mail")
    def test_crear_credenciales_no_envia_password_en_texto_plano(self, mock_send_mail):
        with self.captureOnCommitCallbacks(execute=True):
            VinculacionService.crear_credenciales(
                data={
                    'username': 'seguro.cv@esmic.edu.co',
                    'email': 'seguro.cv@esmic.edu.co',
                    'password': 'Temporal123*',
                },
                ejecutor=self.ejecutor,
            )
        mock_send_mail.assert_called_once()
        _, args, kwargs = mock_send_mail.mock_calls[0]
        mensaje_enviado = args[1] if len(args) > 1 else kwargs.get('message', '')
        self.assertNotIn('Temporal123*', mensaje_enviado)

    # ---------------- activar / desactivar / reactivar ----------------

    def test_desactivar_usuario(self):
        VinculacionService.desactivar_usuario(self.usuario.id, ejecutor=self.ejecutor)
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.is_active)

    def test_activar_usuario(self):
        VinculacionService.desactivar_usuario(self.usuario.id, ejecutor=self.ejecutor)
        VinculacionService.activar_usuario(self.usuario.id, ejecutor=self.ejecutor)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_active)

    def test_reactivar_usuario_delega_en_activar(self):
        VinculacionService.desactivar_usuario(self.usuario.id, ejecutor=self.ejecutor)
        VinculacionService.reactivar_usuario(self.usuario.id, ejecutor=self.ejecutor)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_active)

    def test_desactivar_usuario_inexistente_lanza_404(self):
        with self.assertRaises(Http404):
            VinculacionService.desactivar_usuario(999999, ejecutor=self.ejecutor)

    def test_activar_usuario_inexistente_lanza_404(self):
        with self.assertRaises(Http404):
            VinculacionService.activar_usuario(999999, ejecutor=self.ejecutor)

    # ---------------- reasignar_persona_a_usuario ----------------

    def test_reasignar_persona_a_usuario(self):
        nueva_persona = Persona.objects.create(
            grado=self.grado, nombre='Nueva', apellido='Persona',
            documento='CV-3', celular='3000000003', correo='nueva.cv@esmic.edu.co',
        )
        nueva_asignacion = VinculacionService.reasignar_persona_a_usuario(
            usuario_id=self.usuario.id,
            nueva_persona_id=nueva_persona.id,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(nueva_asignacion.persona_id, nueva_persona.id)
        self.assertTrue(nueva_asignacion.estado)
        self.asignacion.refresh_from_db()
        self.assertFalse(self.asignacion.estado)
        self.assertIsNotNone(self.asignacion.fecha_fin)

    def test_reasignar_a_la_misma_persona_es_idempotente(self):
        resultado = VinculacionService.reasignar_persona_a_usuario(
            usuario_id=self.usuario.id,
            nueva_persona_id=self.persona.id,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(resultado.id, self.asignacion.id)
        self.assertEqual(
            UsuarioXPersona.objects.filter(usuario=self.usuario).count(), 1
        )

    def test_reasignar_no_deja_dos_asignaciones_activas(self):
        otra_persona = Persona.objects.create(
            grado=self.grado, nombre='Otra', apellido='Vez',
            documento='CV-4', celular='3000000004', correo='otravez.cv@esmic.edu.co',
        )
        VinculacionService.reasignar_persona_a_usuario(
            usuario_id=self.usuario.id,
            nueva_persona_id=otra_persona.id,
            ejecutor=self.ejecutor,
        )
        activas = UsuarioXPersona.objects.filter(
            usuario=self.usuario, estado=True
        ).count()
        self.assertEqual(activas, 1)
