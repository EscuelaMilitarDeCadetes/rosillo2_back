from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuarios.models import (
    Usuario,
    RolPlataforma,
    RolXUsuario,
)
from django.core.cache import cache


class UsuarioViewSetTests(TestCase):

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.rol_soporte = RolPlataforma.objects.create(
            nombre_rol="SOPORTE",
            descripcion="Administrador"
        )
        self.rol_supervisor = RolPlataforma.objects.create(
            nombre_rol="SUPERVISOR",
            descripcion="Solo lectura"
        )
        self.admin = Usuario.objects.create_user(
            username="admin@esmic.edu.co",
            email="admin@esmic.edu.co",
            password="Admin123*",
            is_active=True
        )
        RolXUsuario.objects.create(
            usuario=self.admin,
            rol=self.rol_soporte,
            estado=True
        )
        self.usuario = Usuario.objects.create_user(
            username="usuario@esmic.edu.co",
            email="usuario@esmic.edu.co",
            password="Password123*",
            is_active=True
        )
        RolXUsuario.objects.create(
            usuario=self.usuario,
            rol=self.rol_supervisor,
            estado=True
        )
        login = self.client.post(
            reverse("login-formal"),
            {
                "username": "admin@esmic.edu.co",
                "password": "Admin123*"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )    

    # ----------------------------------------------------
    # GET /usuarios/inactivos/
    # ----------------------------------------------------

    def test_listar_usuarios_inactivos(self):
        self.usuario.is_active = False
        self.usuario.save()
        url = reverse("usuarios-usuarios-inactivos")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        ids = [u["id"] for u in response.data]
        self.assertIn(
            self.usuario.id,
            ids
        )
        self.assertNotIn(
            self.admin.id,
            ids
        )

    # ----------------------------------------------------
    # GET /usuarios/admin-dashboard/
    # ----------------------------------------------------

    def test_dashboard(self):
        self.usuario.is_active = False
        self.usuario.save()
        url = reverse("usuarios-dashboard")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIn(
            "usuarios_activos",
            response.data
        )
        self.assertIn(
            "usuarios_inactivos",
            response.data
        )
        self.assertIn(
            "roles_disponibles",
            response.data
        )

    # ----------------------------------------------------
    # GET /usuarios/{id}/roles-activos/
    # ----------------------------------------------------

    def test_roles_activos(self):
        url = reverse(
            "usuarios-roles-activos",
            args=[self.usuario.id]
        )
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data),
            1
        )
        self.assertEqual(
            response.data[0]["rol_nombre"],
            "SUPERVISOR"
        )
        
    def test_delete_no_permitido_sobre_usuario(self):
        """
        UsuarioViewSet es un viewsets.ViewSet puro: no define destroy(),
        por lo tanto DELETE debe responder 405, nunca borrar físicamente
        la fila. El soft-delete real vive en desactivar_usuario (action).
        """
        response = self.client.delete(f'/api/usuarios/usuarios/{self.usuario.id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_no_permitido_sobre_usuario(self):
        """
        Mismo motivo: al no definir update(), cualquier intento de PUT
        debe ser rechazado por el framework, no silenciosamente ignorado.
        """
        response = self.client.put(
            f'/api/usuarios/usuarios/{self.usuario.id}/',
            {'username': 'intento_modificacion'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_no_permitido_sobre_usuario_list(self):
        """
        UsuarioViewSet tampoco define create(): la creación se delega
        por completo a UsuarioFacade/integración (RN-06), no debe existir
        una ruta POST directa sobre este endpoint.
        """
        response = self.client.post(
            '/api/usuarios/usuarios/',
            {'username': 'nuevo@esmic.edu.co', 'password': 'Password123*'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)