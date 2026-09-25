from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.calificacion_selector import CalificacionSelector
from apps.investigacion_formal.selectors.tipo_calificacion_selector import TipoCalificacionSelector
from apps.investigacion_formal.selectors.proyecto_x_convocatoria_selector import (
    ProyectoXConvocatoriaSelector,
)


class CalificacionValidator:

    @staticmethod
    def validar_creacion(fase_id, aplicar_id, observacion=None):
        CalificacionValidator._validar_fase(fase_id)
        CalificacionValidator._validar_aplicar(aplicar_id)
        CalificacionValidator._validar_observacion(observacion)
        CalificacionValidator._validar_unicidad(fase_id, aplicar_id)

    @staticmethod
    def validar_calificacion(observacion, aprobado):
        """Reglas para el acto de calificar una fase ya creada (aprobado/observacion)."""
        if aprobado is None:
            raise ValidationError({"aprobado": "Debe indicar si la fase fue aprobada o no."})
        CalificacionValidator._validar_observacion(observacion, requerida=not aprobado)

    @staticmethod
    def _validar_fase(fase_id):
        if not fase_id:
            raise ValidationError({"fase": "La fase de calificación es obligatoria."})
        if not TipoCalificacionSelector.existe(fase_id):
            raise ValidationError({"fase": f"No existe un TipoCalificacion con id={fase_id}."})


    @staticmethod
    def _validar_aplicar(aplicar_id):
        if not aplicar_id:
            raise ValidationError(
                {"aplicar": "El proyecto-convocatoria a calificar es obligatorio."}
            )
        if not ProyectoXConvocatoriaSelector.existe(aplicar_id):
            raise ValidationError(
                {"aplicar": f"No existe un ProyectoXConvocatoria con id={aplicar_id}."}
            )

    @staticmethod
    def _validar_observacion(observacion, requerida=False):
        if requerida and (not observacion or not observacion.strip()):
            raise ValidationError(
                {"observacion": "Debe indicar una observación cuando la fase no es aprobada."}
            )
        if observacion and len(observacion) > 1000:
            raise ValidationError(
                {"observacion": "La observación supera el máximo de 1000 caracteres."}
            )

    @staticmethod
    def _validar_unicidad(fase_id, aplicar_id, excluir_id=None):
        if CalificacionSelector.existe_calificacion(fase_id, aplicar_id, excluir_id=excluir_id):
            raise ValidationError(
                "Ya existe una calificación registrada para esta fase en este "
                "proyecto-convocatoria."
            )