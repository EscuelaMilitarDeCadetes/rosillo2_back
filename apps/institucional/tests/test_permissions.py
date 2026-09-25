# apps/institucional/tests/test_permissions.py
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
            descripcion="Auditor y personal administrativo"
        )
        self.rol_asesor = RolPlataforma.objects.create(
            nombre_rol="ASESOR",
            descripcion="Asesor de investigación"
        )
        self.rol_facultad = RolPlataforma.objects.create(
            nombre_rol="FACULTAD",
            descripcion="Coordinador de investigación"
        )
        self.rol_grupo = RolPlataforma.objects.create(
            nombre_rol="GRUPO",
            descripcion="Lider de grupo de investigacion"
        )
        self.rol_cinterno = RolPlataforma.objects.create(
            nombre_rol="CINTERNO",
            descripcion="Asesor de convocatorias internas"
        )
        self.rol_cexterno = RolPlataforma.objects.create(
            nombre_rol="CEXTERNO",
            descripcion="Asesor de convocatorias externas"
        )
        self.rol_decano = RolPlataforma.objects.create(
            nombre_rol="DECANO",
            descripcion="CEO de facultad"
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
        # ---------- Usuario ASESOR ----------
        self.asesor = Usuario.objects.create_user(
            username="asesor@esmic.edu.co",
            email="asesor@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.asesor,
            rol=self.rol_asesor,
            estado=True
        )
        # ---------- Usuario FACULTAD ----------
        self.facultad = Usuario.objects.create_user(
            username="facultad@esmic.edu.co",
            email="facultad@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.facultad,
            rol=self.rol_facultad,
            estado=True
        )
        # ---------- Usuario GRUPO ----------
        self.grupo = Usuario.objects.create_user(
            username="grupo@esmic.edu.co",
            email="grupo@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.grupo,
            rol=self.rol_grupo,
            estado=True
        )
        # ---------- Usuario CINTERNO ----------
        self.cinterno = Usuario.objects.create_user(
            username="cinterno@esmic.edu.co",
            email="cinterno@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.cinterno,
            rol=self.rol_cinterno,
            estado=True
        )
        # ---------- Usuario CEXTERNO ----------
        self.cexterno = Usuario.objects.create_user(
            username="cexterno@esmic.edu.co",
            email="cexterno@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.cexterno,
            rol=self.rol_cexterno,
            estado=True
        )
        # ---------- Usuario DECANO ----------
        self.decano = Usuario.objects.create_user(
            username="decano@esmic.edu.co",
            email="decano@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(
            usuario=self.decano,
            rol=self.rol_decano,
            estado=True
        )
        # ---------- Usuario sin rol ----------
        self.sin_rol = Usuario.objects.create_user(
            username="sinrol@esmic.edu.co",
            email="sinrol@esmic.edu.co",
            password="Password123*",
        )
        # ---------- Roles adicionales para los tests "no_puede_acceder" ----------
        self.rol_estudiante = RolPlataforma.objects.create(
            nombre_rol="ESTUDIANTE", descripcion="Estudiante"
        )
        self.rol_gerente = RolPlataforma.objects.create(
            nombre_rol="GERENTE", descripcion="Gerente de proyecto"
        )
        self.rol_jurado = RolPlataforma.objects.create(
            nombre_rol="JURADO", descripcion="Jurado evaluador"
        )
        self.rol_tutor = RolPlataforma.objects.create(
            nombre_rol="TUTOR", descripcion="Tutor de proceso formativo"
        )
        self.estudiante = Usuario.objects.create_user(
            username="estudiante@esmic.edu.co",
            email="estudiante@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(usuario=self.estudiante, rol=self.rol_estudiante, estado=True)
        self.gerente = Usuario.objects.create_user(
            username="gerente@esmic.edu.co",
            email="gerente@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(usuario=self.gerente, rol=self.rol_gerente, estado=True)
        self.jurado = Usuario.objects.create_user(
            username="jurado@esmic.edu.co",
            email="jurado@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(usuario=self.jurado, rol=self.rol_jurado, estado=True)
        self.tutor = Usuario.objects.create_user(
            username="tutor@esmic.edu.co",
            email="tutor@esmic.edu.co",
            password="Password123*",
        )
        RolXUsuario.objects.create(usuario=self.tutor, rol=self.rol_tutor, estado=True)        
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
        
    def test_asesor_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "asesor@esmic.edu.co",
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
        
    def test_facultad_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "facultad@esmic.edu.co",
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
        
    def test_grupo_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "grupo@esmic.edu.co",
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
        
    def test_cinterno_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "cinterno@esmic.edu.co",
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
        
    def test_cexterno_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "cexterno@esmic.edu.co",
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
        
    def test_decano_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "decano@esmic.edu.co",
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
            
    def test_estudiante_no_puede_acceder(self):
        login = self.client.post(
            reverse('login-formativa'),
            {
                "username": "estudiante@esmic.edu.co",
                "password": "Password123*"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
            
    def test_gerente_no_puede_acceder(self):
        login = self.client.post(
            reverse('login-formal'),
            {
                "username": "gerente@esmic.edu.co",
                "password": "Password123*"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
            
    def test_jurado_no_puede_acceder(self):
        login = self.client.post(
            reverse('login-formativa'),
            {
                "username": "jurado@esmic.edu.co",
                "password": "Password123*"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
            
    def test_tutor_no_puede_acceder(self):
        login = self.client.post(
            reverse('login-formativa'),
            {
                "username": "tutor@esmic.edu.co",
                "password": "Password123*"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
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