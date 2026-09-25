from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.services.rol_grupo_service import RolGrupoService


class RolGrupoServiceTests(TestCase):

    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )

    def test_crear_rol_grupo_exitoso(self):
        rol = RolGrupoService.crear('Investigador Principal', self.ejecutor)
        self.assertEqual(rol.cargo, 'Investigador Principal')

    def test_crear_rol_grupo_duplicado_falla(self):
        RolGrupoService.crear('Investigador Principal', self.ejecutor)
        with self.assertRaises(ValidationError):
            RolGrupoService.crear('investigador principal', self.ejecutor)

    def test_crear_rol_grupo_vacio_falla(self):
        with self.assertRaises(ValidationError):
            RolGrupoService.crear('   ', self.ejecutor)

    def test_actualizar_rol_grupo_exitoso(self):
        rol = RolGrupoService.crear('Investigador Principal', self.ejecutor)
        actualizado = RolGrupoService.actualizar(rol.pk, 'Coinvestigador', self.ejecutor)
        self.assertEqual(actualizado.cargo, 'Coinvestigador')