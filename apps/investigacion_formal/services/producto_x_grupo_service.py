from django.db import transaction

from apps.investigacion_formal.models import ProductoXGrupo
from apps.investigacion_formal.selectors.producto_x_grupo_selector import ProductoXGrupoSelector
from apps.investigacion_formal.validators.producto_x_grupo_validator import ProductoXGrupoValidator
from apps.common.services.historial_service import HistorialService


class ProductoXGrupoService:

    @staticmethod
    def listar():
        return ProductoXGrupoSelector.listar()

    @staticmethod
    def obtener(producto_x_grupo_id):
        return ProductoXGrupoSelector.obtener(producto_x_grupo_id)

    @staticmethod
    def obtener_por_producto_minciencias(producto_minciencias_id):
        return ProductoXGrupoSelector.obtener_por_producto_minciencias(producto_minciencias_id)

    @staticmethod
    def listar_por_grupo_minciencias(grupo_minciencias_id):
        return ProductoXGrupoSelector.listar_por_grupo_minciencias(grupo_minciencias_id)

    @staticmethod
    def listar_por_tipo_producto(tipo_producto_id):
        return ProductoXGrupoSelector.listar_por_tipo_producto(tipo_producto_id)

    @staticmethod
    @transaction.atomic
    def crear(producto_minciencias_id, grupo_minciencias_id, tipo_producto_id, ejecutor):
        ProductoXGrupoValidator.validar_creacion(
            producto_minciencias_id, grupo_minciencias_id, tipo_producto_id
        )
        producto_x_grupo = ProductoXGrupo.objects.create(
            producto_minciencias_id=producto_minciencias_id,
            grupo_minciencias_id=grupo_minciencias_id,
            tipo_producto_id=tipo_producto_id,
        )
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se asoció el producto "
            f"'{producto_x_grupo.producto_minciencias.nombre_producto}' al grupo "
            f"'{producto_x_grupo.grupo_minciencias.nombre_grupo_minciencias}' "
            f"(id={producto_x_grupo.pk}).",
            objeto=producto_x_grupo,
        )
        return producto_x_grupo

    @staticmethod
    @transaction.atomic
    def actualizar(producto_x_grupo_id, producto_minciencias_id, grupo_minciencias_id,
                    tipo_producto_id, ejecutor):
        producto_x_grupo = ProductoXGrupoSelector.obtener(producto_x_grupo_id)
        ProductoXGrupoValidator.validar_actualizacion(
            producto_x_grupo_id, producto_minciencias_id, grupo_minciencias_id, tipo_producto_id
        )
        producto_x_grupo.producto_minciencias_id = producto_minciencias_id
        producto_x_grupo.grupo_minciencias_id = grupo_minciencias_id
        producto_x_grupo.tipo_producto_id = tipo_producto_id
        producto_x_grupo.save(update_fields=[
            'producto_minciencias', 'grupo_minciencias', 'tipo_producto',
        ])
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se actualizó la asociación producto-grupo id={producto_x_grupo.pk}.",
            objeto=producto_x_grupo,
        )
        return producto_x_grupo