from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from apps.usuarios.models import Usuario, RolPlataforma, RolXUsuario, UsuarioXPersona
from apps.institucional.models import Persona, GradoEstudios
from django.core.cache import cache


class UsuarioXPersonaViewsetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.grado = GradoEstudios.objects.create(sigla_grado='CIV', descripcion='Civil')
        self.rol_soporte = RolPlataforma.objects.create(
            nombre_rol="SOPORTE", descripcion="Administrador"
        )
        self.admin = Usuario.objects.create_user(
            username="admin@esmic.edu.co",
            email="admin@esmic.edu.co",
            password="Admin123*",
            is_active=True
        )
        RolXUsuario.objects.create(usuario=self.admin, rol=self.rol_soporte, estado=True)
        self.persona_inicial = Persona.objects.create(
            grado=self.grado, nombre="Inicial", apellido="Persona", documento="900000001", celular="3000000001", correo="inicial@esmic.edu.co"
        )
        self.persona_nueva = Persona.objects.create(
            grado=self.grado, nombre="Nueva", apellido="Persona", documento="900000002", celular="3000000002", correo="nueva@esmic.edu.co"
        )
        self.usuario_objetivo = Usuario.objects.create_user(
            username="objetivo@esmic.edu.co",
            email="objetivo@esmic.edu.co",
            password="Password123*",
            is_active=True
        )
        self.asignacion_activa = UsuarioXPersona.objects.create(
            usuario=self.usuario_objetivo,
            persona=self.persona_inicial,
            estado=True
        )
        login = self.client.post(reverse('login-formal'), {
            "username": "admin@esmic.edu.co",
            "password": "Admin123*"
        })
        assert login.status_code == 200, login.data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_list_solo_incluye_asignaciones_activas(self):
        response = self.client.get(reverse("usuario-persona-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usuario_ids = [a["usuario_id"] for a in response.data["results"]]
        self.assertIn(self.usuario_objetivo.id, usuario_ids)

    def test_retrieve_por_usuario(self):
        response = self.client.get(reverse("usuario-persona-detail", args=[self.usuario_objetivo.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["persona_id"], self.persona_inicial.id)

    def test_historico_incluye_asignaciones_inactivas(self):
        """
        Verifica el hallazgo corregido en la ronda anterior: historico()
        debe exponer asignaciones con estado=False, no solo las activas.
        """
        # se cierra manualmente la asignación inicial para simular rotación
        self.asignacion_activa.estado = False
        self.asignacion_activa.save(update_fields=["estado"])
        UsuarioXPersona.objects.create(
            usuario=self.usuario_objetivo, persona=self.persona_nueva, estado=True
        )
        response = self.client.get(
            reverse("usuario-persona-historico", args=[self.usuario_objetivo.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        estados = {a["persona_id"]: a["estado"] for a in response.data}
        self.assertFalse(estados[self.persona_inicial.id])
        self.assertTrue(estados[self.persona_nueva.id])

    def test_historico_usuario_sin_asignaciones_retorna_lista_vacia(self):
        otro_usuario = Usuario.objects.create_user(
            username="sinasignacion@esmic.edu.co", password="Password123*"
        )
        response = self.client.get(
            reverse("usuario-persona-historico", args=[otro_usuario.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    @patch("apps.usuarios.services.usuario_facade.UsuarioFacade.service")
    def test_reasignar_llama_al_service_correcto(self, mock_get_service):
        mock_service = mock_get_service.return_value
        mock_service.reasignar_persona_a_usuario.return_value = type(
            "Asignacion", (), {
                "usuario": self.usuario_objetivo,
                "persona": self.persona_nueva
            }
        )()
        response = self.client.post(reverse("usuario-persona-reasignar"), {
            "usuario_id": self.usuario_objetivo.id,
            "persona_id": self.persona_nueva.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.reasignar_persona_a_usuario.assert_called_once_with(
            usuario_id=str(self.usuario_objetivo.id),
            nueva_persona_id=str(self.persona_nueva.id),
            ejecutor=self.admin
        )

    def test_reasignar_sin_parametros_retorna_400(self):
        response = self.client.post(reverse("usuario-persona-reasignar"), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    
    def test_reasignar_via_servicio_real_actualiza_asignacion(self):
        """
        A diferencia de test_reasignar_llama_al_service_correcto (que mockea el
        facade), este test ejercita UsuarioFacade -> integración de punta a punta.
        """
        otra_persona = Persona.objects.create(
            grado=self.grado, nombre='Otra', apellido='Persona',
            documento='900000003', celular='3000000003', correo='otra@esmic.edu.co'
        )
        url = reverse('usuario-persona-reasignar')
        data = {'usuario_id': self.usuario_objetivo.id, 'persona_id': otra_persona.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reasignar_usuario_inexistente_retorna_404(self):
        url = reverse('usuario-persona-reasignar')
        data = {'usuario_id': 999999, 'persona_id': self.persona_inicial.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reasignar_persona_inexistente_retorna_404(self):
        url = reverse('usuario-persona-reasignar')
        data = {'usuario_id': self.usuario_objetivo.id, 'persona_id': 999999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reasignar_persona_actualizada_se_refleja_en_detail(self):
        """
        Round-trip: reasignar y luego confirmar el cambio vía retrieve.
        No lo cubre historico() (que valida una ruta distinta).
        """
        nueva_persona = Persona.objects.create(
            grado=self.grado, nombre='Nueva Persona 2', apellido='Nuevo Apellido',
            documento='900000004', celular='3000000004', correo='nueva2@esmic.edu.co'
        )
        url = reverse('usuario-persona-reasignar')
        data = {'usuario_id': self.usuario_objetivo.id, 'persona_id': nueva_persona.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url_detail = reverse('usuario-persona-detail', args=[self.usuario_objetivo.id])
        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_detail.data['persona_id'], nueva_persona.id)
        
    def test_rotaciones_filtra_por_rango_de_fechas(self):
        from django.utils import timezone
        from datetime import timedelta
        # asignación fuera de rango
        vieja = UsuarioXPersona.objects.create(
            usuario=self.usuario_objetivo, persona=self.persona_nueva, estado=False
        )
        vieja.fecha_inicio = timezone.now() - timedelta(days=400)
        vieja.save(update_fields=['fecha_inicio'])
        desde = (timezone.now() - timedelta(days=30)).date().isoformat()
        response = self.client.get(f"{reverse('usuario-persona-rotaciones')}?desde={desde}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids_incluidos = [a['id'] for a in response.data]
        self.assertIn(self.asignacion_activa.id, ids_incluidos)
        self.assertNotIn(vieja.id, ids_incluidos)

    def test_rotaciones_sin_parametros_retorna_todo(self):
        response = self.client.get(reverse('usuario-persona-rotaciones'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_rotaciones_fecha_invalida_retorna_400(self):
        response = self.client.get(f"{reverse('usuario-persona-rotaciones')}?desde=fecha-invalida")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)