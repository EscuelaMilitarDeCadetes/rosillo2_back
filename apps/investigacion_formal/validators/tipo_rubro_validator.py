from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.tipo_rubro_selector import TipoRubroSelector


class TipoRubroValidator:

    @staticmethod
    def validar_creacion(nombre_rubro):
        TipoRubroValidator._validar_nombre(nombre_rubro)
        TipoRubroValidator._validar_unicidad(nombre_rubro)

    @staticmethod
    def validar_actualizacion(tipo_rubro_id, nombre_rubro):
        TipoRubroValidator._validar_nombre(nombre_rubro)
        TipoRubroValidator._validar_unicidad(nombre_rubro, excluir_id=tipo_rubro_id)

    @staticmethod
    def _validar_nombre(nombre_rubro):
        if not nombre_rubro or not nombre_rubro.strip():
            raise ValidationError({"nombre_rubro": "El nombre del rubro es obligatorio."})
        if len(nombre_rubro) > 50:
            raise ValidationError({"nombre_rubro": "El nombre supera el máximo de 50 caracteres."})

    @staticmethod
    def _validar_unicidad(nombre_rubro, excluir_id=None):
        if TipoRubroSelector.existe_nombre(nombre_rubro, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_rubro": f"Ya existe el tipo de rubro '{nombre_rubro}'."}
            )