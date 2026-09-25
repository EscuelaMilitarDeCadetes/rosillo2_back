#apps/crm/tests/test_permissions.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from apps.usuarios.models import (
    Usuario,
    RolPlataforma,
    RolXUsuario,
)


class PermissionTests(TestCase):

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        # ---------- Roles ----------
        self.rol_soporte = RolPlataforma.objects.create(
            nombre_rol="SOPORTE",
            descripcion="Administrador"
        )
        self.rol_supervisor = RolPlataforma.objects.create(
            nombre_rol="SUPERVISOR",
            descripcion="Solo lectura"
        )
        # ---------- Usuario SOPORTE ----------
        self.soporte = Usuario.objects.create_user(
            username="soporte@esmic.edu.co",
            email="soporte@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.soporte,
            rol=self.rol_soporte,
            estado=True
        )        
        
        # ---------- Usuario SUPERVISOR ----------
        self.supervisor = Usuario.objects.create_user(
            username="supervisor@esmic.edu.co",
            email="supervisor@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.supervisor,
            rol=self.rol_supervisor,
            estado=True
        )
        # ---------- Usuario sin rol ----------
        self.sin_rol = Usuario.objects.create_user(
            username="sinrol@esmic.edu.co",
            email="sinrol@esmic.edu.co",
            password="Password123*",
        )
        self.url = reverse("usuarios-list")
        
    def test_soporte_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "soporte@esmic.edu.co",
                "password": "Password123*"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
            
    def test_supervisor_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "supervisor@esmic.edu.co",
                "password": "Password123*"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        
    def test_usuario_sin_rol_no_puede_acceder(self):
        login = self.client.post(
            reverse("login-formal"),
            {"username": "sinrol@esmic.edu.co", "password": "Password123*"}
        )
        # El gate por ámbito bloquea el login antes de emitir token:
        # no hay 'access' que usar, así que el 403 se valida aquí.
        self.assertEqual(login.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", login.data)
        
    def test_usuario_anonimo_no_puede_acceder(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )