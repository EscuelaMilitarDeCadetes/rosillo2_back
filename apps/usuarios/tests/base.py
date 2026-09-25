from django.test import TestCase
from apps.institucional.models.grado_estudios import GradoEstudios
from apps.usuarios.models.rol_plataforma import RolPlataforma
from apps.usuarios.models.rol_x_usuario import RolXUsuario
from rest_framework.test import APIClient
from apps.usuarios.models import Usuario, UsuarioXPersona
from apps.institucional.models import Persona

class BaseUsuarioTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()        
        self.grado = GradoEstudios.objects.create(sigla_grado='CIV', descripcion='Civil')
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')
        rol_soporte = RolPlataforma.objects.create(
            nombre_rol='SOPORTE', descripcion='Administrador'
        )
        RolXUsuario.objects.create(usuario=self.usuario, rol=rol_soporte, estado=True)
        self.persona = Persona.objects.create(
            grado=self.grado,
            nombre='Persona prueba',
            apellido='Apellido',
            documento='900000001',
            celular='3000000001',
            correo='personaprueba@esmic.edu.co',
        )
        self.persona_id = self.persona.id
        self.asignacion = UsuarioXPersona.objects.create(usuario=self.usuario, persona_id=self.persona_id, estado=True)
        self.client.force_authenticate(user=self.usuario)