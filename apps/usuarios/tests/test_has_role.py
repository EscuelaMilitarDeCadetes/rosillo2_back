# apps/usuarios/tests/test_has_role.py
from django.test import TestCase
from apps.usuarios.models import Usuario, RolPlataforma, RolXUsuario


class HasRoleTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='hasrole_test@esmic.edu.co',
            email='hasrole_test@esmic.edu.co',
            password='password123',
        )
        self.rol_cinterno = RolPlataforma.objects.create(
            nombre_rol='CINTERNO',
            descripcion='Convocatorias internas',
        )

    def test_has_role_con_rol_activo_devuelve_true(self):
        RolXUsuario.objects.create(
            usuario=self.usuario,
            rol=self.rol_cinterno,
            estado=True,
        )
        self.assertTrue(self.usuario.has_role('CINTERNO'))

    def test_has_role_con_rol_inexistente_devuelve_false(self):
        # El usuario no tiene ningún RolXUsuario para 'DECANO'.
        self.assertFalse(self.usuario.has_role('DECANO'))

    def test_has_role_con_rol_inactivo_devuelve_false(self):
        RolXUsuario.objects.create(
            usuario=self.usuario,
            rol=self.rol_cinterno,
            estado=False,
        )
        self.assertFalse(self.usuario.has_role('CINTERNO'))