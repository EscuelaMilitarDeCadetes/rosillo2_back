from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.services.grado_estudios_service import GradoEstudiosService


class GradoEstudiosServiceTests(TestCase):

    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )

    def test_crear_grado_exitoso(self):
        grado = GradoEstudiosService.crear('MG', 'Magister', self.ejecutor)
        self.assertEqual(grado.sigla_grado, 'MG')

    def test_crear_grado_sigla_duplicada_falla(self):
        GradoEstudiosService.crear('MG', 'Magister', self.ejecutor)
        with self.assertRaises(ValidationError):
            GradoEstudiosService.crear('mg', 'Otro Magister', self.ejecutor)

    def test_crear_grado_sigla_muy_larga_falla(self):
        with self.assertRaises(ValidationError):
            GradoEstudiosService.crear('DEMASIADO', 'Descripción', self.ejecutor)

    def test_actualizar_grado_exitoso(self):
        grado = GradoEstudiosService.crear('MG', 'Magister', self.ejecutor)
        actualizado = GradoEstudiosService.actualizar(
            grado.pk, 'MSC', 'Master of Science', self.ejecutor
        )
        self.assertEqual(actualizado.sigla_grado, 'MSC')

    def test_actualizar_grado_sigla_duplicada_con_otro_falla(self):
        GradoEstudiosService.crear('MG', 'Magister', self.ejecutor)
        grado2 = GradoEstudiosService.crear('DR', 'Doctorado', self.ejecutor)
        with self.assertRaises(ValidationError):
            GradoEstudiosService.actualizar(grado2.pk, 'MG', 'Doctorado', self.ejecutor)

    def test_listar_grados(self):
        GradoEstudiosService.crear('MG', 'Magister', self.ejecutor)
        GradoEstudiosService.crear('DR', 'Doctorado', self.ejecutor)
        grados = GradoEstudiosService.listar()
        self.assertEqual(grados.count(), 2)