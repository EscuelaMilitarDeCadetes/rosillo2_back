from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.registro_horas_selector import RegistroHorasSelector
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)


class RegistroHorasValidator:

    @staticmethod
    def validar_creacion(proceso_id, horas_requeridas=120):
        RegistroHorasValidator._validar_proceso(proceso_id)
        RegistroHorasValidator._validar_horas_requeridas(horas_requeridas)
        RegistroHorasValidator._validar_unicidad_control(proceso_id)

    @staticmethod
    def validar_ajuste_horas_requeridas(control, nuevas_horas_requeridas):
        """Ajuste manual excepcional del mínimo exigido (ej. resolución de coordinación)."""
        RegistroHorasValidator._validar_horas_requeridas(nuevas_horas_requeridas)
        if nuevas_horas_requeridas < control.horas_acumuladas:
            raise ValidationError(
                {"horas_requeridas": (
                    "Las horas requeridas no pueden quedar por debajo de las horas "
                    "ya acumuladas y validadas."
                )}
            )

    @staticmethod
    def _validar_proceso(proceso_id):
        if not proceso_id:
            raise ValidationError({"proceso": "El proceso formativo es obligatorio."})
        if not ProcesoFormativoSelector.existe(proceso_id):
            raise ValidationError({"proceso": f"No existe un ProcesoFormativo con id={proceso_id}."})

    @staticmethod
    def _validar_horas_requeridas(horas_requeridas):
        if horas_requeridas is None:
            raise ValidationError({"horas_requeridas": "Las horas requeridas son obligatorias."})
        try:
            valor = float(horas_requeridas)
        except (TypeError, ValueError):
            raise ValidationError({"horas_requeridas": "Las horas requeridas deben ser numéricas."})
        if valor <= 0:
            raise ValidationError({"horas_requeridas": "Las horas requeridas deben ser mayores a cero."})

    @staticmethod
    def _validar_unicidad_control(proceso_id):
        if RegistroHorasSelector.existe_para_proceso(proceso_id):
            raise ValidationError("Este proceso formativo ya tiene un control de horas registrado.")