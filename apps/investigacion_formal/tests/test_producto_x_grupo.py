from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.models import TipoProducto
from apps.investigacion_formal.services.producto_minciencias_service import (
    ProductoMincienciasService,
)
from apps.investigacion_formal.services.grupo_minciencias_service import GrupoMincienciasService
from apps.investigacion_formal.services.producto_x_grupo_service import ProductoXGrupoService


class ProductoXGrupoServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.producto_minciencias = ProductoMincienciasService.crear(
            nombre_producto='Producto Base', nomenclatura='PB-1',
            peso=10, vigencia=4, ejecutor=self.ejecutor,
        )
        self.grupo_minciencias = GrupoMincienciasService.crear(
            nombre_grupo_minciencias='Grupo Base', ejecutor=self.ejecutor,
        )
        self.tipo_producto = TipoProducto.objects.create(
            tipo_producto='Artículo científico', aplica=True,
        )

    def test_crear_producto_x_grupo_exitoso(self):
        registro = ProductoXGrupoService.crear(
            producto_minciencias_id=self.producto_minciencias.pk,
            grupo_minciencias_id=self.grupo_minciencias.pk,
            tipo_producto_id=self.tipo_producto.pk,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(registro.producto_minciencias_id, self.producto_minciencias.pk)

    def test_crear_producto_x_grupo_combinacion_duplicada_falla(self):
        ProductoXGrupoService.crear(
            producto_minciencias_id=self.producto_minciencias.pk,
            grupo_minciencias_id=self.grupo_minciencias.pk,
            tipo_producto_id=self.tipo_producto.pk,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProductoXGrupoService.crear(
                producto_minciencias_id=self.producto_minciencias.pk,
                grupo_minciencias_id=self.grupo_minciencias.pk,
                tipo_producto_id=self.tipo_producto.pk,
                ejecutor=self.ejecutor,
            )

    def test_crear_producto_x_grupo_producto_minciencias_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            ProductoXGrupoService.crear(
                producto_minciencias_id=999999,
                grupo_minciencias_id=self.grupo_minciencias.pk,
                tipo_producto_id=self.tipo_producto.pk,
                ejecutor=self.ejecutor,
            )

    def test_actualizar_producto_x_grupo_exitoso(self):
        registro = ProductoXGrupoService.crear(
            producto_minciencias_id=self.producto_minciencias.pk,
            grupo_minciencias_id=self.grupo_minciencias.pk,
            tipo_producto_id=self.tipo_producto.pk,
            ejecutor=self.ejecutor,
        )
        otro_tipo = TipoProducto.objects.create(tipo_producto='Libro', aplica=True)
        actualizado = ProductoXGrupoService.actualizar(
            producto_x_grupo_id=registro.pk,
            producto_minciencias_id=self.producto_minciencias.pk,
            grupo_minciencias_id=self.grupo_minciencias.pk,
            tipo_producto_id=otro_tipo.pk,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.tipo_producto_id, otro_tipo.pk)

    def test_obtener_por_producto_minciencias(self):
        ProductoXGrupoService.crear(
            producto_minciencias_id=self.producto_minciencias.pk,
            grupo_minciencias_id=self.grupo_minciencias.pk,
            tipo_producto_id=self.tipo_producto.pk,
            ejecutor=self.ejecutor,
        )
        encontrado = ProductoXGrupoService.obtener_por_producto_minciencias(
            self.producto_minciencias.pk
        )
        self.assertIsNotNone(encontrado)

    def test_listar_por_grupo_minciencias(self):
        ProductoXGrupoService.crear(
            producto_minciencias_id=self.producto_minciencias.pk,
            grupo_minciencias_id=self.grupo_minciencias.pk,
            tipo_producto_id=self.tipo_producto.pk,
            ejecutor=self.ejecutor,
        )
        resultado = ProductoXGrupoService.listar_por_grupo_minciencias(self.grupo_minciencias.pk)
        self.assertEqual(resultado.count(), 1)