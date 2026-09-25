from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.services.grupo_investigacion_service import GrupoInvestigacionService


class GrupoInvestigacionServiceTests(TestCase):

    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )

    def test_crear_grupo_exitoso(self):
        grupo = GrupoInvestigacionService.crear('Grupo CM', 'CM', 'A1', self.ejecutor)
        self.assertEqual(grupo.sigla_grupo, 'CM')

    def test_crear_grupo_nombre_duplicado_falla(self):
        GrupoInvestigacionService.crear('Grupo CM', 'CM', 'A1', self.ejecutor)
        with self.assertRaises(ValidationError):
            GrupoInvestigacionService.crear('grupo cm', 'CM2', 'A1', self.ejecutor)

    def test_crear_grupo_sigla_duplicada_falla(self):
        GrupoInvestigacionService.crear('Grupo CM', 'CM', 'A1', self.ejecutor)
        with self.assertRaises(ValidationError):
            GrupoInvestigacionService.crear('Grupo Rendimiento fisico militar', 'CM', 'B', self.ejecutor)

    def test_actualizar_grupo_exitoso(self):
        grupo = GrupoInvestigacionService.crear('Grupo CM', 'CM', 'A1', self.ejecutor)
        actualizado = GrupoInvestigacionService.actualizar(
            grupo.pk, 'Grupo Ciencias Militares', 'GCM', 'A1', self.ejecutor
        )
        self.assertEqual(actualizado.sigla_grupo, 'GCM')

    def test_listar_grupos_usuario_sin_vinculacion_retorna_none(self):
        resultado = GrupoInvestigacionService.listar_grupos_usuario(usuario_id=99999)
        self.assertIsNone(resultado)