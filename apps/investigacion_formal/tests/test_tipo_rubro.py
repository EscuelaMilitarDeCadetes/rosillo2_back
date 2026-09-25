from rest_framework.exceptions import ValidationError
from django.test import TestCase

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.tipo_rubro_service import TipoRubroService


class TipoRubroServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def test_crear_tipo_rubro_exitoso(self):
        rubro = TipoRubroService.crear(nombre_rubro='Personal', aplica=True, ejecutor=self.ejecutor)
        self.assertEqual(rubro.nombre_rubro, 'Personal')

    def test_crear_tipo_rubro_nombre_duplicado_falla(self):
        TipoRubroService.crear(nombre_rubro='Equipos', aplica=True, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            TipoRubroService.crear(nombre_rubro='equipos', aplica=True, ejecutor=self.ejecutor)

    def test_crear_tipo_rubro_nombre_vacio_falla(self):
        with self.assertRaises(ValidationError):
            TipoRubroService.crear(nombre_rubro='   ', aplica=True, ejecutor=self.ejecutor)

    def test_actualizar_tipo_rubro_exitoso(self):
        rubro = TipoRubroService.crear(nombre_rubro='Viáticos', aplica=True, ejecutor=self.ejecutor)
        actualizado = TipoRubroService.actualizar(
            tipo_rubro_id=rubro.pk, nombre_rubro='Viáticos y Transporte', aplica=True, ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.nombre_rubro, 'Viáticos y Transporte')

    def test_actualizar_tipo_rubro_nombre_duplicado_con_otro_falla(self):
        TipoRubroService.crear(nombre_rubro='Materiales', aplica=True, ejecutor=self.ejecutor)
        rubro2 = TipoRubroService.crear(nombre_rubro='Software', aplica=True, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            TipoRubroService.actualizar(
                tipo_rubro_id=rubro2.pk, nombre_rubro='Materiales', aplica=True, ejecutor=self.ejecutor,
            )

    def test_listar_tipos_rubro(self):
        TipoRubroService.crear(nombre_rubro='Rubro 1', aplica=True, ejecutor=self.ejecutor)
        TipoRubroService.crear(nombre_rubro='Rubro 2', aplica=True, ejecutor=self.ejecutor)
        self.assertEqual(TipoRubroService.listar().count(), 2)