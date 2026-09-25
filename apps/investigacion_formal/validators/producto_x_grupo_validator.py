# apps/investigacion_formal/validators/producto_x_grupo_validator.py
from rest_framework.exceptions import ValidationError
from apps.investigacion_formal.selectors.producto_minciencias_selector import ProductoMincienciasSelector
from apps.investigacion_formal.selectors.grupo_minciencias_selector import GrupoMincienciasSelector
from apps.investigacion_formal.selectors.tipo_producto_selector import TipoProductoSelector
from apps.investigacion_formal.selectors.producto_x_grupo_selector import ProductoXGrupoSelector


class ProductoXGrupoValidator:

    @staticmethod
    def validar_creacion(producto_minciencias_id, grupo_minciencias_id, tipo_producto_id):
        ProductoXGrupoValidator._validar_producto_minciencias(producto_minciencias_id)
        ProductoXGrupoValidator._validar_grupo_minciencias(grupo_minciencias_id)
        ProductoXGrupoValidator._validar_tipo_producto(tipo_producto_id)
        ProductoXGrupoValidator._validar_unicidad(
            producto_minciencias_id, grupo_minciencias_id, tipo_producto_id
        )

    @staticmethod
    def validar_actualizacion(producto_x_grupo_id, producto_minciencias_id,
                               grupo_minciencias_id, tipo_producto_id):
        ProductoXGrupoValidator._validar_producto_minciencias(producto_minciencias_id)
        ProductoXGrupoValidator._validar_grupo_minciencias(grupo_minciencias_id)
        ProductoXGrupoValidator._validar_tipo_producto(tipo_producto_id)
        ProductoXGrupoValidator._validar_unicidad(
            producto_minciencias_id, grupo_minciencias_id, tipo_producto_id,
            excluir_id=producto_x_grupo_id,
        )

    @staticmethod
    def _validar_producto_minciencias(producto_minciencias_id):
        if not producto_minciencias_id:
            raise ValidationError({"producto_minciencias": "El producto Minciencias es obligatorio."})
        if not ProductoMincienciasSelector.existe(producto_minciencias_id):
            raise ValidationError(
                {"producto_minciencias": f"No existe un ProductoMinciencias con id={producto_minciencias_id}."}
            )

    @staticmethod
    def _validar_grupo_minciencias(grupo_minciencias_id):
        if not grupo_minciencias_id:
            raise ValidationError({"grupo_minciencias": "El grupo Minciencias es obligatorio."})
        if not GrupoMincienciasSelector.existe(grupo_minciencias_id):
            raise ValidationError(
                {"grupo_minciencias": f"No existe un GrupoMinciencias con id={grupo_minciencias_id}."}
            )

    @staticmethod
    def _validar_tipo_producto(tipo_producto_id):
        if not tipo_producto_id:
            raise ValidationError({"tipo_producto": "El tipo de producto es obligatorio."})
        if not TipoProductoSelector.existe(tipo_producto_id):
            raise ValidationError(
                {"tipo_producto": f"No existe un TipoProducto con id={tipo_producto_id}."}
            )

    @staticmethod
    def _validar_unicidad(producto_minciencias_id, grupo_minciencias_id, tipo_producto_id, excluir_id=None):
        if ProductoXGrupoSelector.existe_combinacion(
            producto_minciencias_id, grupo_minciencias_id, tipo_producto_id, excluir_id=excluir_id
        ):
            raise ValidationError(
                "Ya existe esta misma combinación de producto Minciencias, grupo "
                "Minciencias y tipo de producto."
            )