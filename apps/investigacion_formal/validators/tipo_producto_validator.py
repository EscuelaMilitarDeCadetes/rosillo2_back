from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.tipo_producto_selector import TipoProductoSelector


class TipoProductoValidator:

    @staticmethod
    def validar_creacion(tipo_producto, aplica):
        TipoProductoValidator._validar_nombre(tipo_producto)
        TipoProductoValidator._validar_aplica(aplica)
        TipoProductoValidator._validar_unicidad(tipo_producto)

    @staticmethod
    def validar_actualizacion(tipo_producto_id, tipo_producto, aplica):
        TipoProductoValidator._validar_nombre(tipo_producto)
        TipoProductoValidator._validar_aplica(aplica)
        TipoProductoValidator._validar_unicidad(tipo_producto, excluir_id=tipo_producto_id)

    @staticmethod
    def _validar_nombre(tipo_producto):
        if not tipo_producto or not tipo_producto.strip():
            raise ValidationError({"tipo_producto": "El nombre del tipo de producto es obligatorio."})
        if len(tipo_producto) > 200:
            raise ValidationError({"tipo_producto": "El nombre supera el máximo de 200 caracteres."})

    @staticmethod
    def _validar_aplica(aplica):
        if aplica is None:
            raise ValidationError({"aplica": "Debe indicar si este tipo de producto aplica actualmente."})

    @staticmethod
    def _validar_unicidad(tipo_producto, excluir_id=None):
        if TipoProductoSelector.existe_nombre(tipo_producto, excluir_id=excluir_id):
            raise ValidationError(
                {"tipo_producto": f"Ya existe el tipo de producto '{tipo_producto}'."}
            )