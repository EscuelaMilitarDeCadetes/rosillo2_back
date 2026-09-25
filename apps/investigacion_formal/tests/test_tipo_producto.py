from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.tipo_producto_service import TipoProductoService


class TipoProductoServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def test_crear_tipo_producto_exitoso(self):
        tipo = TipoProductoService.crear(
            tipo_producto='Artículo científico', aplica=True, ejecutor=self.ejecutor,
        )
        self.assertTrue(tipo.aplica)

    def test_crear_tipo_producto_nombre_duplicado_falla(self):
        TipoProductoService.crear(
            tipo_producto='Tipo Único', aplica=True, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            TipoProductoService.crear(
                tipo_producto='tipo único', aplica=False, ejecutor=self.ejecutor,
            )

    def test_crear_tipo_producto_aplica_nulo_falla(self):
        with self.assertRaises(ValidationError):
            TipoProductoService.crear(
                tipo_producto='Tipo Sin Aplica', aplica=None, ejecutor=self.ejecutor,
            )

    def test_actualizar_tipo_producto_exitoso(self):
        tipo = TipoProductoService.crear(
            tipo_producto='Nombre Original', aplica=True, ejecutor=self.ejecutor,
        )
        actualizado = TipoProductoService.actualizar(
            tipo_producto_id=tipo.pk,
            tipo_producto='Nombre Corregido',
            aplica=False,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.tipo_producto, 'Nombre Corregido')
        self.assertFalse(actualizado.aplica)