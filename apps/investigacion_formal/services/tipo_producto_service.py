from django.db import transaction

from apps.investigacion_formal.models import TipoProducto
from apps.investigacion_formal.selectors.tipo_producto_selector import TipoProductoSelector
from apps.investigacion_formal.validators.tipo_producto_validator import TipoProductoValidator
from apps.common.services.historial_service import HistorialService


class TipoProductoService:

    @staticmethod
    def listar():
        return TipoProductoSelector.listar()

    @staticmethod
    def obtener(tipo_producto_id):
        return TipoProductoSelector.obtener(tipo_producto_id)

    @staticmethod
    @transaction.atomic
    def crear(tipo_producto, aplica, ejecutor):
        TipoProductoValidator.validar_creacion(tipo_producto, aplica)
        tipo = TipoProducto.objects.create(
            tipo_producto=tipo_producto.strip(),
            aplica=aplica,
        )
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se creó el tipo de producto '{tipo.tipo_producto}' "
            f"(id={tipo.pk}).",
            objeto=tipo,
        )
        return tipo

    @staticmethod
    @transaction.atomic
    def actualizar(tipo_producto_id, tipo_producto, aplica, ejecutor):
        tipo = TipoProductoSelector.obtener(tipo_producto_id)
        TipoProductoValidator.validar_actualizacion(tipo_producto_id, tipo_producto, aplica)
        tipo.tipo_producto = tipo_producto.strip()
        tipo.aplica = aplica
        tipo.save(update_fields=['tipo_producto', 'aplica'])
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se actualizó el tipo de producto '{tipo.tipo_producto}' "
            f"(id={tipo.pk}).",
            objeto=tipo,
        )
        return tipo