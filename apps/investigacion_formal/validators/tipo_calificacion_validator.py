from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.tipo_calificacion_selector import TipoCalificacionSelector


class TipoCalificacionValidator:

    @staticmethod
    def validar_creacion(tipo_calificacion, descripcion, evaluacion, orden_fase):
        TipoCalificacionValidator._validar_nombre(tipo_calificacion)
        TipoCalificacionValidator._validar_descripcion(descripcion)
        TipoCalificacionValidator._validar_evaluacion(evaluacion)
        TipoCalificacionValidator._validar_orden(orden_fase)
        TipoCalificacionValidator._validar_unicidad_nombre(tipo_calificacion)
        TipoCalificacionValidator._validar_unicidad_orden(orden_fase)

    @staticmethod
    def validar_actualizacion(tipo_calificacion_id, tipo_calificacion, descripcion, evaluacion, orden_fase):
        TipoCalificacionValidator._validar_nombre(tipo_calificacion)
        TipoCalificacionValidator._validar_descripcion(descripcion)
        TipoCalificacionValidator._validar_evaluacion(evaluacion)
        TipoCalificacionValidator._validar_orden(orden_fase)
        TipoCalificacionValidator._validar_unicidad_nombre(
            tipo_calificacion, excluir_id=tipo_calificacion_id
        )
        TipoCalificacionValidator._validar_unicidad_orden(
            orden_fase, excluir_id=tipo_calificacion_id
        )

    @staticmethod
    def _validar_nombre(tipo_calificacion):
        if not tipo_calificacion or not tipo_calificacion.strip():
            raise ValidationError({"tipo_calificacion": "El nombre del tipo de calificación es obligatorio."})
        if len(tipo_calificacion) > 30:
            raise ValidationError(
                {"tipo_calificacion": "El nombre supera el máximo de 30 caracteres."}
            )

    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            raise ValidationError({"descripcion": "La descripción es obligatoria."})
        if len(descripcion) > 150:
            raise ValidationError({"descripcion": "La descripción supera el máximo de 150 caracteres."})

    @staticmethod
    def _validar_evaluacion(evaluacion):
        if evaluacion is None:
            raise ValidationError(
                {"evaluacion": "Debe indicar si esta fase es de tipo evaluación."}
            )

    @staticmethod
    def _validar_orden(orden_fase):
        if orden_fase is None:
            raise ValidationError({"orden_fase": "El orden de la fase es obligatorio."})
        if not isinstance(orden_fase, int) or orden_fase < 1:
            raise ValidationError({"orden_fase": "El orden de la fase debe ser un entero mayor o igual a 1."})

    @staticmethod
    def _validar_unicidad_nombre(tipo_calificacion, excluir_id=None):
        if TipoCalificacionSelector.existe_nombre(tipo_calificacion, excluir_id=excluir_id):
            raise ValidationError(
                {"tipo_calificacion": f"Ya existe el tipo de calificación '{tipo_calificacion}'."}
            )

    @staticmethod
    def _validar_unicidad_orden(orden_fase, excluir_id=None):
        if TipoCalificacionSelector.existe_orden(orden_fase, excluir_id=excluir_id):
            raise ValidationError(
                {"orden_fase": f"Ya existe una fase registrada con el orden {orden_fase}."}
            )