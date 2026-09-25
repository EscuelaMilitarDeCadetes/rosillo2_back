from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.usuarios.models import Usuario, RolPlataforma, RolXUsuario


class MeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create_user(
            username="rolinfo@esmic.edu.co",
            email="rolinfo@esmic.edu.co",
            password="Passw0rd!2024",
        )
        self.rol_supervisor = RolPlataforma.objects.create(
            nombre_rol="SUPERVISOR", descripcion="test"
        )
        RolXUsuario.objects.create(
            usuario=self.usuario, rol=self.rol_supervisor, estado=True
        )

    def test_me_devuelve_roles_activos(self):
        login = self.client.post(reverse('login-formal'), {
            "username": self.usuario.username,
            "password": "Passw0rd!2024",
        })
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.usuario.username)
        self.assertIn("SUPERVISOR", response.data["roles"])

    def test_me_requiere_autenticacion(self):
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, 401)