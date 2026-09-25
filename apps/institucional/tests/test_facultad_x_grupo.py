from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.models import GrupoInvestigacion, FacultadEscuela
from apps.institucional.services.facultad_x_grupo_service import FacultadXGrupoService


class FacultadXGrupoServiceTests(TestCase):

    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )
        self.grupo = GrupoInvestigacion.objects.create(
            nombre_grupo='Grupo CM', sigla_grupo='CM', clasificacion_grupo='A1'
        )
        self.facultad = FacultadEscuela.objects.create(
            nombre_facultad='Facultad de Ingeniería', abreviatura='FING'
        )

    def test_crear_relacion_exitoso(self):
        relacion = FacultadXGrupoService.crear(self.grupo.pk, self.facultad.pk, self.ejecutor)
        self.assertEqual(relacion.grupo, self.grupo)
        self.assertEqual(relacion.facultad, self.facultad)

    def test_crear_relacion_duplicada_falla(self):
        FacultadXGrupoService.crear(self.grupo.pk, self.facultad.pk, self.ejecutor)
        with self.assertRaises(ValidationError):
            FacultadXGrupoService.crear(self.grupo.pk, self.facultad.pk, self.ejecutor)

    def test_crear_relacion_grupo_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            FacultadXGrupoService.crear(99999, self.facultad.pk, self.ejecutor)

    def test_crear_relacion_facultad_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            FacultadXGrupoService.crear(self.grupo.pk, 99999, self.ejecutor)

    def test_obtener_grupo_de_facultad(self):
        FacultadXGrupoService.crear(self.grupo.pk, self.facultad.pk, self.ejecutor)
        grupo_obtenido = FacultadXGrupoService.obtener_grupo_de_facultad(self.facultad.pk)
        self.assertEqual(grupo_obtenido, self.grupo)

    def test_obtener_grupo_de_facultad_sin_relacion_retorna_none(self):
        grupo_obtenido = FacultadXGrupoService.obtener_grupo_de_facultad(self.facultad.pk)
        self.assertIsNone(grupo_obtenido)