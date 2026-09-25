from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.models import GrupoInvestigacion, FacultadXGrupo
from apps.institucional.services.facultad_escuela_service import FacultadEscuelaService


class FacultadEscuelaServiceTests(TestCase):

    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )

    def test_crear_facultad_exitoso(self):
        facultad = FacultadEscuelaService.crear('Facultad de Ingeniería', 'FING', self.ejecutor)
        self.assertEqual(facultad.abreviatura, 'FING')

    def test_crear_facultad_nombre_duplicado_falla(self):
        FacultadEscuelaService.crear('Facultad de Ingeniería', 'FING', self.ejecutor)
        with self.assertRaises(ValidationError):
            FacultadEscuelaService.crear('facultad de ingeniería', 'FING2', self.ejecutor)

    def test_crear_facultad_abreviatura_duplicada_falla(self):
        FacultadEscuelaService.crear('Facultad de Ingeniería', 'FING', self.ejecutor)
        with self.assertRaises(ValidationError):
            FacultadEscuelaService.crear('Facultad de Ciencias', 'FING', self.ejecutor)

    def test_crear_facultad_abreviatura_muy_larga_falla(self):
        with self.assertRaises(ValidationError):
            FacultadEscuelaService.crear('Facultad X', 'ABCDEFG', self.ejecutor)

    def test_actualizar_facultad_exitoso(self):
        facultad = FacultadEscuelaService.crear('Facultad de Ingeniería', 'FING', self.ejecutor)
        actualizada = FacultadEscuelaService.actualizar(
            facultad.pk, 'Facultad de Ingenierías', 'FINGS', self.ejecutor
        )
        self.assertEqual(actualizada.abreviatura, 'FINGS')

    def test_listar_facultades_grupo(self):
        grupo = GrupoInvestigacion.objects.create(
            nombre_grupo='Grupo CM', sigla_grupo='CM', clasificacion_grupo='A1'
        )
        facultad = FacultadEscuelaService.crear('Facultad X', 'FX', self.ejecutor)
        FacultadXGrupo.objects.create(grupo=grupo, facultad=facultad)
        facultades = FacultadEscuelaService.listar_facultades_grupo(grupo_id=grupo.pk)
        self.assertIn(facultad, list(facultades))