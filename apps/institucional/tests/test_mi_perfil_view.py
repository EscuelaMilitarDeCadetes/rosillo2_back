from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.usuarios.models import Usuario, UsuarioXPersona, RolPlataforma, RolXUsuario
from apps.institucional.models import Persona, GradoEstudios


class MiPerfilViewTests(TestCase):
    """
    Sigue el patrón de MeViewTests (apps/usuarios/tests/test_me_view.py):
    login real contra login-formal/login-formativa (no force_authenticate),
    para probar el endpoint tal como lo golpea el frontend.
    """

    def setUp(self):
        self.client = APIClient()
        self.grado = GradoEstudios.objects.create(sigla_grado="CIV", descripcion="Civil")
        self.otro_grado = GradoEstudios.objects.create(sigla_grado="ADM", descripcion="Administracion")

        # Un ESTUDIANTE (formativa) representa el caso típico de "Mi Perfil":
        # un usuario sin ningún rol administrativo, que antes no podía ver
        # ni editar sus propios datos por PersonaViewSet (EsSoporte-only).
        self.usuario = Usuario.objects.create_user(
            username="perfilprueba@esmic.edu.co",
            email="perfilprueba@esmic.edu.co",
            password="Passw0rd!2024",
        )
        rol_estudiante = RolPlataforma.objects.create(
            nombre_rol="ESTUDIANTE", descripcion="test"
        )
        RolXUsuario.objects.create(usuario=self.usuario, rol=rol_estudiante, estado=True)

        self.persona = Persona.objects.create(
            grado=self.grado,
            nombre="Nombre prueba",
            apellido="Apellido prueba",
            documento="900000001",
            celular="3000000001",
            correo="perfilprueba@esmic.edu.co",
            cvlac="http://cvlac/original",
        )
        UsuarioXPersona.objects.create(usuario=self.usuario, persona=self.persona, estado=True)

        login = self.client.post(reverse('login-formativa'), {
            "username": self.usuario.username,
            "password": "Passw0rd!2024",
        })
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_get_devuelve_los_datos_de_mi_persona(self):
        response = self.client.get(reverse('mi-perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["documento"], "900000001")
        self.assertEqual(response.data["correo"], "perfilprueba@esmic.edu.co")
        self.assertEqual(response.data["nombre"], "Nombre prueba")
        self.assertEqual(response.data["grado_sigla"], "CIV")

    def test_requiere_autenticacion(self):
        client = APIClient()
        response = client.get(reverse('mi-perfil'))
        self.assertEqual(response.status_code, 401)

    def test_patch_actualiza_los_campos_editables(self):
        response = self.client.patch(reverse('mi-perfil'), {
            "grado": self.otro_grado.id,
            "nombre": "Nombre nuevo",
            "apellido": "Apellido nuevo",
            "celular": "3000000099",
            "cvlac": "http://cvlac/nuevo",
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.persona.refresh_from_db()
        self.assertEqual(self.persona.grado_id, self.otro_grado.id)
        self.assertEqual(self.persona.nombre, "Nombre nuevo")
        self.assertEqual(self.persona.apellido, "Apellido nuevo")
        self.assertEqual(self.persona.celular, "3000000099")
        self.assertEqual(self.persona.cvlac, "http://cvlac/nuevo")

    def test_patch_ignora_intentos_de_cambiar_documento_y_correo(self):
        response = self.client.patch(reverse('mi-perfil'), {
            "documento": "999999999",
            "correo": "otro@esmic.edu.co",
            "nombre": "Nombre nuevo",
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.persona.refresh_from_db()
        # Se mantienen intactos aunque vengan en el payload:
        self.assertEqual(self.persona.documento, "900000001")
        self.assertEqual(self.persona.correo, "perfilprueba@esmic.edu.co")
        # El resto del payload sí se aplica:
        self.assertEqual(self.persona.nombre, "Nombre nuevo")
        # La respuesta tampoco los expone como modificados:
        self.assertEqual(response.data["documento"], "900000001")
        self.assertEqual(response.data["correo"], "perfilprueba@esmic.edu.co")

    def test_patch_no_afecta_a_otras_personas(self):
        otra_persona = Persona.objects.create(
            grado=self.grado,
            nombre="Otra",
            apellido="Persona",
            documento="900000002",
            celular="3000000002",
            correo="otrapersona@esmic.edu.co",
        )
        self.client.patch(reverse('mi-perfil'), {"nombre": "Cambiado"}, format='json')
        otra_persona.refresh_from_db()
        self.assertEqual(otra_persona.nombre, "Otra")

    def test_usuario_sin_persona_asociada_devuelve_404(self):
        usuario_sin_persona = Usuario.objects.create_user(
            username="sinpersona@esmic.edu.co",
            email="sinpersona@esmic.edu.co",
            password="Passw0rd!2024",
        )
        rol_estudiante = RolPlataforma.objects.get(nombre_rol="ESTUDIANTE")
        RolXUsuario.objects.create(usuario=usuario_sin_persona, rol=rol_estudiante, estado=True)

        client = APIClient()
        login = client.post(reverse('login-formativa'), {
            "username": usuario_sin_persona.username,
            "password": "Passw0rd!2024",
        })
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = client.get(reverse('mi-perfil'))
        self.assertEqual(response.status_code, 404)