# apps/investigacion_formativa/validators/evaluacion_proceso_validator.py
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.evaluacion_proceso_selector import EvaluacionProcesoSelector

NOTA_MINIMA = 0.0
NOTA_MAXIMA = 5.0
NOTA_APROBATORIA = 3.5


class EvaluacionProcesoValidator:
    """
    No se expone actualizar() ni eliminar(), porque una evaluación
    ya emitida es un registro de auditoría académica. Por
    eso este validator solo tiene validar_creacion().
    """

    @staticmethod
    def validar_creacion(evaluador_id, instancia_etapa_id, nota, peso, concepto, aprobado, resultado):
        EvaluacionProcesoValidator._validar_concepto(concepto)
        EvaluacionProcesoValidator._validar_nota(nota)
        EvaluacionProcesoValidator._validar_peso(peso)
        EvaluacionProcesoValidator._validar_resultado(resultado)
        EvaluacionProcesoValidator.validar_consistencia_aprobado(aprobado, nota)
        EvaluacionProcesoValidator._validar_unicidad(evaluador_id, instancia_etapa_id)

    @staticmethod
    def validar_consistencia_aprobado(aprobado, nota):
        """El indicador 'aprobado' debe ser coherente con la nota registrada."""
        if aprobado and nota < NOTA_APROBATORIA:
            raise ValidationError(
                {"aprobado": f"No se puede marcar como aprobado con una nota inferior a {NOTA_APROBATORIA}."}
            )
        if not aprobado and nota >= NOTA_APROBATORIA:
            raise ValidationError(
                {"aprobado": f"La nota registrada ({nota}) corresponde a una evaluación aprobada; revise el indicador."}
            )

    @staticmethod
    def _validar_concepto(concepto):
        if not concepto or not concepto.strip():
            raise ValidationError({"concepto": "El concepto de la evaluación es obligatorio."})
        if len(concepto) > 100:
            raise ValidationError({"concepto": "El concepto supera el máximo de 100 caracteres."})

    @staticmethod
    def _validar_nota(nota):
        if nota is None:
            raise ValidationError({"nota": "La nota es obligatoria."})
        try:
            valor = float(nota)
        except (TypeError, ValueError):
            raise ValidationError({"nota": "La nota debe ser numérica."})
        if valor < NOTA_MINIMA or valor > NOTA_MAXIMA:
            raise ValidationError(
                {"nota": f"La nota debe estar entre {NOTA_MINIMA} y {NOTA_MAXIMA}."}
            )

    @staticmethod
    def _validar_peso(peso):
        if peso is None:
            raise ValidationError({"peso": "El peso de la evaluación es obligatorio."})
        try:
            valor = float(peso)
        except (TypeError, ValueError):
            raise ValidationError({"peso": "El peso debe ser numérico."})
        if valor <= 0:
            raise ValidationError({"peso": "El peso debe ser mayor a 0."})

    @staticmethod
    def _validar_unicidad(evaluador_id, instancia_etapa_id, excluir_id=None):
        if EvaluacionProcesoSelector.existe_evaluador_en_instancia(
            evaluador_id, instancia_etapa_id, excluir_id=excluir_id
        ):
            raise ValidationError(
                "Este evaluador ya registró una evaluación para esta etapa del proceso."
            )

    @staticmethod
    def _validar_resultado(resultado):
        if not resultado or not resultado.strip():
            raise ValidationError({"resultado": "El resultado de la evaluación es obligatorio."})