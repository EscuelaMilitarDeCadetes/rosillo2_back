from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.producto_minciencias_selector import ProductoMincienciasSelector


class ProductoMincienciasValidator:

    @staticmethod
    def validar_creacion(nombre_producto, nomenclatura, peso, vigencia):
        ProductoMincienciasValidator._validar_nombre(nombre_producto)
        ProductoMincienciasValidator._validar_nomenclatura(nomenclatura)
        ProductoMincienciasValidator._validar_peso(peso)
        ProductoMincienciasValidator._validar_vigencia(vigencia)
        ProductoMincienciasValidator._validar_unicidad_nombre(nombre_producto)
        ProductoMincienciasValidator._validar_unicidad_nomenclatura(nomenclatura)

    @staticmethod
    def validar_actualizacion(producto_minciencias_id, nombre_producto, nomenclatura, peso, vigencia):
        ProductoMincienciasValidator._validar_nombre(nombre_producto)
        ProductoMincienciasValidator._validar_nomenclatura(nomenclatura)
        ProductoMincienciasValidator._validar_peso(peso)
        ProductoMincienciasValidator._validar_vigencia(vigencia)
        ProductoMincienciasValidator._validar_unicidad_nombre(
            nombre_producto, excluir_id=producto_minciencias_id
        )
        ProductoMincienciasValidator._validar_unicidad_nomenclatura(
            nomenclatura, excluir_id=producto_minciencias_id
        )

    @staticmethod
    def _validar_nombre(nombre_producto):
        if not nombre_producto or not nombre_producto.strip():
            raise ValidationError({"nombre_producto": "El nombre del producto es obligatorio."})
        if len(nombre_producto) > 200:
            raise ValidationError({"nombre_producto": "El nombre supera el máximo de 200 caracteres."})

    @staticmethod
    def _validar_nomenclatura(nomenclatura):
        if not nomenclatura or not nomenclatura.strip():
            raise ValidationError({"nomenclatura": "La nomenclatura es obligatoria."})
        if len(nomenclatura) > 20:
            raise ValidationError({"nomenclatura": "La nomenclatura supera el máximo de 20 caracteres."})

    @staticmethod
    def _validar_peso(peso):
        if peso is None:
            raise ValidationError({"peso": "El peso del producto es obligatorio."})
        if not isinstance(peso, int) or peso < 0:
            raise ValidationError({"peso": "El peso debe ser un entero no negativo."})

    @staticmethod
    def _validar_vigencia(vigencia):
        if vigencia is None:
            raise ValidationError({"vigencia": "La vigencia del producto es obligatoria."})
        if not isinstance(vigencia, int) or vigencia < 0:
            raise ValidationError({"vigencia": "La vigencia debe ser un entero no negativo."})

    @staticmethod
    def _validar_unicidad_nombre(nombre_producto, excluir_id=None):
        if ProductoMincienciasSelector.existe_nombre(nombre_producto, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_producto": f"Ya existe el producto '{nombre_producto}'."}
            )

    @staticmethod
    def _validar_unicidad_nomenclatura(nomenclatura, excluir_id=None):
        if ProductoMincienciasSelector.existe_nomenclatura(nomenclatura, excluir_id=excluir_id):
            raise ValidationError(
                {"nomenclatura": f"Ya existe un producto con la nomenclatura '{nomenclatura}'."}
            )