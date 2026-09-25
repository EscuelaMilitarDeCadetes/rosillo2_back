from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.punto_control_selector import PuntoControlSelector


class PuntoControlValidator:

    @staticmethod
    def validar_creacion(control, peso):
        PuntoControlValidator._validar_control(control)
        PuntoControlValidator._validar_peso(peso)
        PuntoControlValidator._validar_unicidad(control)

    @staticmethod
    def _validar_control(control):
        if not control or not control.strip():
            raise ValidationError({"control": "La descripción del punto de control es obligatoria."})
        if len(control) > 255:
            raise ValidationError({"control": "El punto de control supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_peso(peso):
        if peso is None:
            raise ValidationError({"peso": "El peso del punto de control es obligatorio."})
        try:
            valor = float(peso)
        except (TypeError, ValueError):
            raise ValidationError({"peso": "El peso debe ser numérico."})
        if valor < 0:
            raise ValidationError({"peso": "El peso no puede ser negativo."})

    @staticmethod
    def _validar_unicidad(control, excluir_id=None):
        if PuntoControlSelector.existe_control(control, excluir_id=excluir_id):
            raise ValidationError(
                {"control": f"Ya existe un punto de control con el texto '{control}'."}
            )