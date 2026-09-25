from django.http import Http404
from apps.usuarios.models import Usuario
from ..services.usuario_service import UsuarioService
from .base import BaseUsuarioTestCase


class UsuarioServiceTests(BaseUsuarioTestCase):
    
    def test_obtener_persona_actual(self):
        persona_actual = UsuarioService.obtener_persona_actual(self.usuario)
        self.assertEqual(persona_actual.id, self.persona.id)
    
    def test_mostrar_todos_usuarios_activos(self):
        usuario_inactivo = Usuario.objects.create_user(
            username="inactivo",
            password="123",
            email="inactivo@esmic.edu.co",
            is_active=False
        )
        activos = UsuarioService.mostrar_todos_usuarios()
        self.assertIn(self.usuario, activos)
        self.assertNotIn(usuario_inactivo, activos)
        
    def test_get_user_data(self):
        usuario = UsuarioService.get_user_data(self.usuario.email)
        self.assertEqual(usuario.id, self.usuario.id)
    
    def test_get_user_data_usuario_inexistente(self):
        with self.assertRaises(Http404):
            UsuarioService.get_user_data("noexiste@esmic.edu.co")        
            
    def test_obtener_persona_actual_sin_asignacion(self):
        usuario = Usuario.objects.create_user(
            username="usuario_sin_persona",
            password="Password123*",
            email="sin_persona@esmic.edu.co"
        )
        self.assertFalse(usuario.asignaciones.exists())
        persona = UsuarioService.obtener_persona_actual(usuario)
        self.assertIsNone(persona)