from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.objetivos_service import ObjetivosService


class ObjetivosServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proyecto = self._crear_proyecto()

    def test_crear_objetivo_general_exitoso(self):
        objetivo = ObjetivosService.crear_objetivo_general(
            proyecto_id=self.proyecto.pk,
            objetivo='Desarrollar un sistema de gestión académica',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(objetivo.clase, 'PRINCIPAL')
        self.assertTrue(objetivo.estado)

    def test_crear_segundo_objetivo_general_para_mismo_proyecto_falla(self):
        ObjetivosService.crear_objetivo_general(
            proyecto_id=self.proyecto.pk,
            objetivo='Objetivo general 1',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ObjetivosService.crear_objetivo_general(
                proyecto_id=self.proyecto.pk,
                objetivo='Objetivo general 2',
                ejecutor=self.ejecutor,
            )

    def test_crear_objetivo_especifico_exitoso(self):
        objetivo = ObjetivosService.crear_objetivo_especifico(
            proyecto_id=self.proyecto.pk,
            objetivo='Diseñar el módulo de reportes',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(objetivo.clase, 'ESPECIFICO')

    def test_crear_objetivo_texto_duplicado_falla(self):
        ObjetivosService.crear_objetivo_especifico(
            proyecto_id=self.proyecto.pk,
            objetivo='Objetivo único',
            ejecutor=self.ejecutor,
        )
        otro_proyecto = self._crear_proyecto(titulo='Otro proyecto')
        with self.assertRaises(ValidationError):
            ObjetivosService.crear_objetivo_especifico(
                proyecto_id=otro_proyecto.pk,
                objetivo='Objetivo único',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_objetivo_exitoso(self):
        objetivo = ObjetivosService.crear_objetivo_especifico(
            proyecto_id=self.proyecto.pk,
            objetivo='Texto original',
            ejecutor=self.ejecutor,
        )
        actualizado = ObjetivosService.actualizar(
            objetivo_id=objetivo.pk,
            objetivo='Texto corregido',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.objetivo, 'Texto corregido')

    def test_eliminar_objetivo_soft_delete(self):
        objetivo = ObjetivosService.crear_objetivo_especifico(
            proyecto_id=self.proyecto.pk,
            objetivo='Objetivo a desactivar',
            ejecutor=self.ejecutor,
        )
        ObjetivosService.eliminar(objetivo.pk, ejecutor=self.ejecutor)
        objetivo.refresh_from_db()
        self.assertFalse(objetivo.estado)

    def test_eliminar_objetivo_ya_desactivado_falla(self):
        objetivo = ObjetivosService.crear_objetivo_especifico(
            proyecto_id=self.proyecto.pk,
            objetivo='Objetivo doble baja',
            ejecutor=self.ejecutor,
        )
        ObjetivosService.eliminar(objetivo.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            ObjetivosService.eliminar(objetivo.pk, ejecutor=self.ejecutor)

    def test_obtener_objetivo_general(self):
        ObjetivosService.crear_objetivo_general(
            proyecto_id=self.proyecto.pk,
            objetivo='Objetivo general de prueba',
            ejecutor=self.ejecutor,
        )
        encontrado = ObjetivosService.obtener_objetivo_general(self.proyecto.pk)
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.clase, 'PRINCIPAL')