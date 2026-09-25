from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.producto_minciencias_service import (
    ProductoMincienciasService,
)


class ProductoMincienciasServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def test_crear_producto_minciencias_exitoso(self):
        producto = ProductoMincienciasService.crear(
            nombre_producto='Artículo de investigación A1',
            nomenclatura='ART-A1',
            peso=10,
            vigencia=4,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(producto.nombre_producto, 'Artículo de investigación A1')
        self.assertEqual(producto.nomenclatura, 'ART-A1')

    def test_crear_producto_minciencias_nombre_duplicado_falla(self):
        ProductoMincienciasService.crear(
            nombre_producto='Producto Único', nomenclatura='PU-1',
            peso=5, vigencia=2, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProductoMincienciasService.crear(
                nombre_producto='producto único', nomenclatura='PU-2',
                peso=5, vigencia=2, ejecutor=self.ejecutor,
            )

    def test_crear_producto_minciencias_nomenclatura_duplicada_falla(self):
        ProductoMincienciasService.crear(
            nombre_producto='Producto A', nomenclatura='NOM-1',
            peso=5, vigencia=2, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProductoMincienciasService.crear(
                nombre_producto='Producto B', nomenclatura='NOM-1',
                peso=5, vigencia=2, ejecutor=self.ejecutor,
            )

    def test_crear_producto_minciencias_peso_negativo_falla(self):
        with self.assertRaises(ValidationError):
            ProductoMincienciasService.crear(
                nombre_producto='Producto Inválido', nomenclatura='PI-1',
                peso=-1, vigencia=2, ejecutor=self.ejecutor,
            )

    def test_actualizar_producto_minciencias_exitoso(self):
        producto = ProductoMincienciasService.crear(
            nombre_producto='Nombre Original', nomenclatura='ORIG-1',
            peso=5, vigencia=2, ejecutor=self.ejecutor,
        )
        actualizado = ProductoMincienciasService.actualizar(
            producto_minciencias_id=producto.pk,
            nombre_producto='Nombre Corregido',
            nomenclatura='CORR-1',
            peso=8,
            vigencia=3,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.nombre_producto, 'Nombre Corregido')
        self.assertEqual(actualizado.peso, 8)

    def test_listar_productos_minciencias(self):
        ProductoMincienciasService.crear(
            nombre_producto='Producto 1', nomenclatura='P1',
            peso=5, vigencia=2, ejecutor=self.ejecutor,
        )
        ProductoMincienciasService.crear(
            nombre_producto='Producto 2', nomenclatura='P2',
            peso=5, vigencia=2, ejecutor=self.ejecutor,
        )
        self.assertEqual(ProductoMincienciasService.listar().count(), 2)