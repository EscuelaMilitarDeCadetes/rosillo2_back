from django.db import transaction

from apps.investigacion_formal.models import ProductoMinciencias
from apps.investigacion_formal.selectors.producto_minciencias_selector import (
    ProductoMincienciasSelector,
)
from apps.investigacion_formal.validators.producto_minciencias_validator import (
    ProductoMincienciasValidator,
)
from apps.common.services.historial_service import HistorialService


class ProductoMincienciasService:

    @staticmethod
    def listar():
        return ProductoMincienciasSelector.listar()

    @staticmethod
    def obtener(producto_minciencias_id):
        return ProductoMincienciasSelector.obtener(producto_minciencias_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre_producto, nomenclatura, peso, vigencia, ejecutor):
        ProductoMincienciasValidator.validar_creacion(nombre_producto, nomenclatura, peso, vigencia)
        producto = ProductoMinciencias.objects.create(
            nombre_producto=nombre_producto.strip(),
            nomenclatura=nomenclatura.strip(),
            peso=peso,
            vigencia=vigencia,
        )
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se creó el producto Minciencias '{producto.nombre_producto}' "
            f"(nomenclatura={producto.nomenclatura}, id={producto.pk}).",
            objeto=producto,
        )
        return producto

    @staticmethod
    @transaction.atomic
    def actualizar(producto_minciencias_id, nombre_producto, nomenclatura, peso, vigencia, ejecutor):
        producto = ProductoMincienciasSelector.obtener(producto_minciencias_id)
        ProductoMincienciasValidator.validar_actualizacion(
            producto_minciencias_id, nombre_producto, nomenclatura, peso, vigencia
        )
        producto.nombre_producto = nombre_producto.strip()
        producto.nomenclatura = nomenclatura.strip()
        producto.peso = peso
        producto.vigencia = vigencia
        producto.save(update_fields=['nombre_producto', 'nomenclatura', 'peso', 'vigencia'])
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se actualizó el producto Minciencias "
            f"'{producto.nombre_producto}' (id={producto.pk}).",
            objeto=producto,
        )
        return producto