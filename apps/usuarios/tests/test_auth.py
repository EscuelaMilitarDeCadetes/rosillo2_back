# apps/usuarios/tests/test_auth.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import Usuario, RolPlataforma, RolXUsuario
from django.core.cache import cache
from django.test import override_settings

from rest_framework_simplejwt.tokens import AccessToken
from apps.usuarios.ambitos import AMBITO_FORMAL, AMBITO_FORMATIVA


class LoginLogoutTests(TestCase):

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.rol_soporte = RolPlataforma.objects.create(
            nombre_rol='SOPORTE',
            descripcion='Gestiona usuarios'
        )
        self.user = Usuario.objects.create_user(
            username='testuser@esmic.edu.co',
            email='testuser@esmic.edu.co',
            password='password123',
            is_active=True
        )
        RolXUsuario.objects.create(
            usuario=self.user,
            rol=self.rol_soporte,
            estado=True
        )

    def test_login_exitoso(self):
        response = self.client.post(reverse('login-formal'), {
            'username': 'testuser@esmic.edu.co',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['ambito'], 'formal')

    def test_login_credenciales_invalidas(self):
        response = self.client.post(reverse('login-formal'), {
            'username': 'testuser@esmic.edu.co',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_usuario_inactivo(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('login-formal'), {
            'username': 'testuser@esmic.edu.co',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_exitoso(self):
        login = self.client.post(reverse('login-formal'), {
            'username': 'testuser@esmic.edu.co',
            'password': 'password123'
        })
        refresh_token = login.data['refresh']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.post(reverse('logout'), {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_sin_refresh_token(self):
        login = self.client.post(reverse('login-formal'), {
            'username': 'testuser@esmic.edu.co',
            'password': 'password123'
        })
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.post(reverse('logout'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_usuario_inexistente(self):
        response = self.client.post(
            reverse("login-formal"),
            {
                "username": "noexiste@esmic.edu.co",
                "password": "Password123*"
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_logout_refresh_invalido(self):
        login = self.client.post(
            reverse("login-formal"),
            {
                "username": "testuser@esmic.edu.co",
                "password": "password123"
            }
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = self.client.post(
            reverse("logout"),
            {
                "refresh": "token_invalido"
            }
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @override_settings()
    def test_login_rate_throttle(self):
        from rest_framework.settings import api_settings
        from django.conf import settings
        original = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login']
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'] = '5/min'
        api_settings.reload()
        try:
            # Los primeros cinco intentos son válidos
            for _ in range(5):
                response = self.client.post(
                    reverse("login-formal"),
                    {
                        "username": "testuser@esmic.edu.co",
                        "password": "password123",
                    }
                )
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK
                )

            # El sexto debe ser bloqueado
            response = self.client.post(
                reverse("login-formal"),
                {
                    "username": "testuser@esmic.edu.co",
                    "password": "password123",
                }
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS
            )
        finally:
            settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login'] = original
            api_settings.reload()

    def test_login_reporta_debe_cambiar_password(self):
        self.user.debe_cambiar_password = True
        self.user.save(update_fields=['debe_cambiar_password'])
        response = self.client.post(reverse('login-formal'), {
            'username': 'testuser@esmic.edu.co',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['debe_cambiar_password'])


class LoginAmbitoTests(TestCase):
    """
    Casos nuevos específicos del doble login: un rol exclusivo de un ámbito
    no puede autenticarse por el endpoint del otro, y un rol compartido
    puede hacerlo por cualquiera de los dos.
    """

    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.rol_estudiante = RolPlataforma.objects.create(
            nombre_rol='ESTUDIANTE', descripcion='Estudiante'
        )
        self.rol_cinterno = RolPlataforma.objects.create(
            nombre_rol='CINTERNO', descripcion='Coordinador interno'
        )
        self.rol_facultad = RolPlataforma.objects.create(
            nombre_rol='FACULTAD', descripcion='Facultad'
        )

        self.estudiante = Usuario.objects.create_user(
            username='estudiante@esmic.edu.co',
            email='estudiante@esmic.edu.co',
            password='password123',
            is_active=True,
        )
        RolXUsuario.objects.create(
            usuario=self.estudiante, rol=self.rol_estudiante, estado=True
        )

        self.cinterno = Usuario.objects.create_user(
            username='cinterno@esmic.edu.co',
            email='cinterno@esmic.edu.co',
            password='password123',
            is_active=True,
        )
        RolXUsuario.objects.create(
            usuario=self.cinterno, rol=self.rol_cinterno, estado=True
        )

        self.facultad = Usuario.objects.create_user(
            username='facultad@esmic.edu.co',
            email='facultad@esmic.edu.co',
            password='password123',
            is_active=True,
        )
        RolXUsuario.objects.create(
            usuario=self.facultad, rol=self.rol_facultad, estado=True
        )

    def test_estudiante_no_puede_entrar_por_login_formal(self):
        response = self.client.post(reverse('login-formal'), {
            'username': 'estudiante@esmic.edu.co',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_estudiante_puede_entrar_por_login_formativa(self):
        response = self.client.post(reverse('login-formativa'), {
            'username': 'estudiante@esmic.edu.co',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ambito'], 'formativa')

    def test_cinterno_no_puede_entrar_por_login_formativa(self):
        response = self.client.post(reverse('login-formativa'), {
            'username': 'cinterno@esmic.edu.co',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cinterno_puede_entrar_por_login_formal(self):
        response = self.client.post(reverse('login-formal'), {
            'username': 'cinterno@esmic.edu.co',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ambito'], 'formal')

    def test_rol_compartido_puede_entrar_por_ambos(self):
        response_formal = self.client.post(reverse('login-formal'), {
            'username': 'facultad@esmic.edu.co',
            'password': 'password123',
        })
        response_formativa = self.client.post(reverse('login-formativa'), {
            'username': 'facultad@esmic.edu.co',
            'password': 'password123',
        })
        self.assertEqual(response_formal.status_code, status.HTTP_200_OK)
        self.assertEqual(response_formativa.status_code, status.HTTP_200_OK)
        self.assertEqual(response_formal.data['ambito'], 'formal')
        self.assertEqual(response_formativa.data['ambito'], 'formativa')
        

class TokenRefreshAmbitoTests(TestCase):
    """
    Verifica que el claim 'ambito' sobrevive a la rotación de refresh
    tokens (ROTATE_REFRESH_TOKENS=True). Es el comportamiento del que
    depende TieneAmbitoFormal/TieneAmbitoFormativa en cada request
    posterior al primer login, así que merece test explícito y no solo
    quedar como comentario en tiene_ambito.py.
    """

    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create_user(
            username="refresh_ambito@esmic.edu.co",
            email="refresh_ambito@esmic.edu.co",
            password="Passw0rd!2024",
        )
        rol = RolPlataforma.objects.create(nombre_rol="SOPORTE", descripcion="test")
        RolXUsuario.objects.create(usuario=self.usuario, rol=rol, estado=True)

    def _login_y_refrescar(self, url_login):
        login = self.client.post(url_login, {
            "username": self.usuario.username,
            "password": "Passw0rd!2024",
        })
        self.assertEqual(login.status_code, 200)

        refresh_original = login.data["refresh"]
        response = self.client.post(reverse("token_refresh"), {"refresh": refresh_original})
        self.assertEqual(response.status_code, 200)
        return response.data["access"]

    def test_ambito_formal_persiste_tras_refresh(self):
        nuevo_access = self._login_y_refrescar(reverse("login-formal"))
        payload = AccessToken(nuevo_access)
        self.assertEqual(payload["ambito"], AMBITO_FORMAL)

    def test_ambito_formativa_persiste_tras_refresh(self):
        nuevo_access = self._login_y_refrescar(reverse("login-formativa"))
        payload = AccessToken(nuevo_access)
        self.assertEqual(payload["ambito"], AMBITO_FORMATIVA)