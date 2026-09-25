#apps/usuarios/tests/test_passwords.py
from datetime import timedelta
from django.utils import timezone          
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from apps.usuarios.models import Usuario, RolPlataforma, RolXUsuario


class PasswordTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(
            username='user@esmic.edu.co',
            email='user@esmic.edu.co',
            password='oldpassword123',
            is_active=True
        )
        rol = RolPlataforma.objects.create(
            nombre_rol='SOPORTE', descripcion='test'
        )
        RolXUsuario.objects.create(
            usuario=self.user, rol=rol, estado=True
        )
        login = self.client.post(reverse('login-formal'), {
            'username': 'user@esmic.edu.co',
            'password': 'oldpassword123'
        })
        self.access_token = login.data['access']

    @patch('apps.common.tasks.send_mail')
    def test_forgot_password_email_registrado(self, mock_mail):
        response = self.client.post(
            '/api/usuarios/password/forgot-password/',
            {'email': 'user@esmic.edu.co'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_token_invalido(self):
        response = self.client.post(
            '/api/usuarios/password/reset-password/',
            {
                'token': 'tokeninvalido',
                'password': 'nueva123456',
                'confirm_password': 'nueva123456'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_exitoso(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        response = self.client.post(
            '/api/usuarios/password/change-password/',
            {
                'old_password': 'oldpassword123',
                'new_password': 'nueva123456'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_contraseña_incorrecta(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        response = self.client.post(
            '/api/usuarios/password/change-password/',
            {
                'old_password': 'wrongpassword',
                'new_password': 'nueva123456'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_reset_password_token_valido(self):
        self.user.token_recuperacion = "token123"
        self.user.token_creado_en = timezone.now()
        self.user.save()
        response = self.client.post(
            "/api/usuarios/password/reset-password/",
            {
                "token": "token123",
                "password": "NuevaPassword123*",
                "confirm_password": "NuevaPassword123*"
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("NuevaPassword123*")
        )
        self.assertIsNone(
            self.user.token_recuperacion
        )
        
    def test_reset_password_token_expirado(self):
        self.user.token_recuperacion = "token123"
        self.user.token_creado_en = (
            timezone.now() - timedelta(hours=2)
        )
        self.user.save()
        response = self.client.post(
            "/api/usuarios/password/reset-password/",
            {
                "token": "token123",
                "password": "NuevaPassword123*",
                "confirm_password": "NuevaPassword123*"
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
    
    def test_change_password_limpia_flag_debe_cambiar(self):
        self.user.debe_cambiar_password = True
        self.user.save(update_fields=['debe_cambiar_password'])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post('/api/usuarios/password/change-password/', {
            'old_password': 'oldpassword123',
            'new_password': 'nueva123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.debe_cambiar_password)