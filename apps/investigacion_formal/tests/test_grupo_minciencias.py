from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.grupo_minciencias_service import GrupoMincienciasService


class GrupoMincienciasServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def test_crear_grupo_minciencias_exitoso(self):
        grupo = GrupoMincienciasService.crear(
            nombre_grupo_minciencias='Productos de Nuevo Conocimiento',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(grupo.nombre_grupo_minciencias, 'Productos de Nuevo Conocimiento')

    def test_crear_grupo_minciencias_nombre_duplicado_falla(self):
        GrupoMincienciasService.crear(
            nombre_grupo_minciencias='Productos de Desarrollo Tecnológico',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            GrupoMincienciasService.crear(
                nombre_grupo_minciencias='productos de desarrollo tecnológico',
                ejecutor=self.ejecutor,
            )

    def test_crear_grupo_minciencias_nombre_vacio_falla(self):
        with self.assertRaises(ValidationError):
            GrupoMincienciasService.crear(
                nombre_grupo_minciencias='   ',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_grupo_minciencias_exitoso(self):
        grupo = GrupoMincienciasService.crear(
            nombre_grupo_minciencias='Nombre Original',
            ejecutor=self.ejecutor,
        )
        actualizado = GrupoMincienciasService.actualizar(
            grupo_minciencias_id=grupo.pk,
            nombre_grupo_minciencias='Nombre Corregido',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.nombre_grupo_minciencias, 'Nombre Corregido')

    def test_actualizar_grupo_minciencias_nombre_duplicado_con_otro_falla(self):
        GrupoMincienciasService.crear(
            nombre_grupo_minciencias='Grupo A', ejecutor=self.ejecutor,
        )
        grupo_b = GrupoMincienciasService.crear(
            nombre_grupo_minciencias='Grupo B', ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            GrupoMincienciasService.actualizar(
                grupo_minciencias_id=grupo_b.pk,
                nombre_grupo_minciencias='Grupo A',
                ejecutor=self.ejecutor,
            )

    def test_listar_grupos_minciencias(self):
        GrupoMincienciasService.crear(nombre_grupo_minciencias='Grupo 1', ejecutor=self.ejecutor)
        GrupoMincienciasService.crear(nombre_grupo_minciencias='Grupo 2', ejecutor=self.ejecutor)
        self.assertEqual(GrupoMincienciasService.listar().count(), 2)