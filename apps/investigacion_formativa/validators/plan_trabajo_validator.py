from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.plan_trabajo_selector import PlanTrabajoSelector
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)

ESTADOS_EDITABLES = {'BORRADOR', 'RECHAZADO'}


class PlanTrabajoValidator:

    @staticmethod
    def validar_creacion(proceso_id, descripcion_general, objetivo_general, actividades_planeadas,
                          fecha_inicio_planeada, fecha_fin_planeada, observaciones=None):
        PlanTrabajoValidator._validar_proceso(proceso_id)
        PlanTrabajoValidator._validar_descripcion_general(descripcion_general)
        PlanTrabajoValidator._validar_objetivo_general(objetivo_general)
        PlanTrabajoValidator._validar_actividades_planeadas(actividades_planeadas)
        PlanTrabajoValidator._validar_fechas(fecha_inicio_planeada, fecha_fin_planeada)
        PlanTrabajoValidator._validar_observaciones(observaciones)

    @staticmethod
    def validar_actualizacion(plan_trabajo, descripcion_general, objetivo_general, actividades_planeadas,
                               fecha_inicio_planeada, fecha_fin_planeada, observaciones=None):
        PlanTrabajoValidator._validar_editable(plan_trabajo)
        PlanTrabajoValidator._validar_descripcion_general(descripcion_general)
        PlanTrabajoValidator._validar_objetivo_general(objetivo_general)
        PlanTrabajoValidator._validar_actividades_planeadas(actividades_planeadas)
        PlanTrabajoValidator._validar_fechas(fecha_inicio_planeada, fecha_fin_planeada)
        PlanTrabajoValidator._validar_observaciones(observaciones)

    @staticmethod
    def validar_envio(plan_trabajo):
        """Réplica del paso BORRADOR/RECHAZADO -> ENVIADO."""
        if plan_trabajo.estado not in ESTADOS_EDITABLES:
            raise ValidationError(
                f"No se puede enviar a revisión un plan de trabajo en estado '{plan_trabajo.estado}'."
            )

    @staticmethod
    def validar_aprobacion(plan_trabajo, aprobado_por_id):
        if plan_trabajo.estado != 'ENVIADO':
            raise ValidationError(
                "Solo se puede aprobar un plan de trabajo que se encuentre en estado 'ENVIADO'."
            )
        PlanTrabajoValidator._validar_aprobado_por(aprobado_por_id)

    @staticmethod
    def validar_rechazo(plan_trabajo, observaciones=None):
        if plan_trabajo.estado != 'ENVIADO':
            raise ValidationError(
                "Solo se puede rechazar un plan de trabajo que se encuentre en estado 'ENVIADO'."
            )
        if not observaciones or not observaciones.strip():
            raise ValidationError(
                {"observaciones": "Debe indicar la razón del rechazo del plan de trabajo."}
            )

    @staticmethod
    def validar_eliminacion(plan_trabajo):
        if plan_trabajo.estado != 'BORRADOR':
            raise ValidationError("Solo se puede eliminar un plan de trabajo en estado 'BORRADOR'.")

    @staticmethod
    def _validar_proceso(proceso_id):
        if not proceso_id:
            raise ValidationError({"proceso": "El proceso formativo es obligatorio."})
        if not ProcesoFormativoSelector.existe(proceso_id):
            raise ValidationError({"proceso": f"No existe un ProcesoFormativo con id={proceso_id}."})
        if PlanTrabajoSelector.existe_para_proceso(proceso_id):
            raise ValidationError("Este proceso formativo ya tiene un plan de trabajo registrado.")

    @staticmethod
    def _validar_editable(plan_trabajo):
        if plan_trabajo.estado not in ESTADOS_EDITABLES:
            raise ValidationError(
                f"No se puede editar un plan de trabajo en estado '{plan_trabajo.estado}'."
            )

    @staticmethod
    def _validar_descripcion_general(descripcion_general):
        if not descripcion_general or not descripcion_general.strip():
            raise ValidationError({"descripcion_general": "La descripción general es obligatoria."})

    @staticmethod
    def _validar_objetivo_general(objetivo_general):
        if not objetivo_general or not objetivo_general.strip():
            raise ValidationError({"objetivo_general": "El objetivo general es obligatorio."})

    @staticmethod
    def _validar_actividades_planeadas(actividades_planeadas):
        if not actividades_planeadas or not actividades_planeadas.strip():
            raise ValidationError({"actividades_planeadas": "Las actividades planeadas son obligatorias."})

    @staticmethod
    def _validar_fechas(fecha_inicio_planeada, fecha_fin_planeada):
        if not fecha_inicio_planeada or not fecha_fin_planeada:
            raise ValidationError(
                "Las fechas de inicio y fin planeadas del plan de trabajo son obligatorias."
            )
        if fecha_fin_planeada < fecha_inicio_planeada:
            raise ValidationError(
                {"fecha_fin_planeada": "La fecha de fin planeada no puede ser anterior a la fecha de inicio planeada."}
            )

    @staticmethod
    def _validar_observaciones(observaciones):
        # Campo opcional (null=True, blank=True); sin restricciones adicionales.
        pass

    @staticmethod
    def _validar_aprobado_por(aprobado_por_id):
        if not aprobado_por_id:
            raise ValidationError({"aprobado_por": "El usuario que aprueba el plan de trabajo es obligatorio."})
        # Import diferido: usuarios no es dependencia directa de investigacion_formativa
        from apps.usuarios.models import Usuario

        if not Usuario.objects.filter(pk=aprobado_por_id).exists():
            raise ValidationError({"aprobado_por": f"No existe un Usuario con id={aprobado_por_id}."})