from django.db import transaction
from django.utils import timezone
from apps.investigacion_formativa.models import PlanTrabajo
from apps.investigacion_formativa.selectors.plan_trabajo_selector import PlanTrabajoSelector
from apps.investigacion_formativa.validators.plan_trabajo_validator import PlanTrabajoValidator
from apps.common.services.historial_service import HistorialService
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)
from apps.investigacion_formativa.services._soporte import (
    notificar,
    usuario_id_estudiante_de_proceso,
    validar_ejecutor_autor_o_gestor_por_proceso,
)


class PlanTrabajoService:

    @staticmethod
    def listar():
        return PlanTrabajoSelector.listar()

    @staticmethod
    def obtener(plan_trabajo_id):
        return PlanTrabajoSelector.obtener(plan_trabajo_id)

    @staticmethod
    def obtener_por_proceso(proceso_id):
        return PlanTrabajoSelector.obtener_por_proceso(proceso_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_id, descripcion_general, objetivo_general, actividades_planeadas,
              fecha_inicio_planeada, fecha_fin_planeada, ejecutor, observaciones=None):
        PlanTrabajoValidator.validar_creacion(
            proceso_id, descripcion_general, objetivo_general, actividades_planeadas,
            fecha_inicio_planeada, fecha_fin_planeada, observaciones,
        )
        proceso = ProcesoFormativoSelector.obtener(proceso_id)
        # El estudiante solo puede crear el plan de trabajo de SU propio
        # proceso; Facultad/Decano pueden hacerlo en su nombre.
        validar_ejecutor_autor_o_gestor_por_proceso(
            proceso, ejecutor, "este plan de trabajo"
        )
        plan = PlanTrabajo.objects.create(
            proceso_id=proceso_id,
            descripcion_general=descripcion_general,
            objetivo_general=objetivo_general,
            actividades_planeadas=actividades_planeadas,
            fecha_inicio_planeada=fecha_inicio_planeada,
            fecha_fin_planeada=fecha_fin_planeada,
            observaciones=observaciones,
            estado='BORRADOR',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el plan de trabajo del proceso '{plan.proceso.titulo}' (id={plan.pk}).",
            objeto=plan,
        )
        return plan

    @staticmethod
    @transaction.atomic
    def actualizar(plan_trabajo_id, descripcion_general, objetivo_general, actividades_planeadas,
                    fecha_inicio_planeada, fecha_fin_planeada, ejecutor, observaciones=None):
        plan = PlanTrabajoSelector.obtener(plan_trabajo_id)
        validar_ejecutor_autor_o_gestor_por_proceso(
            plan.proceso, ejecutor, "este plan de trabajo"
        )
        PlanTrabajoValidator.validar_actualizacion(
            plan, descripcion_general, objetivo_general, actividades_planeadas,
            fecha_inicio_planeada, fecha_fin_planeada, observaciones,
        )
        plan.descripcion_general = descripcion_general
        plan.objetivo_general = objetivo_general
        plan.actividades_planeadas = actividades_planeadas
        plan.fecha_inicio_planeada = fecha_inicio_planeada
        plan.fecha_fin_planeada = fecha_fin_planeada
        plan.observaciones = observaciones
        plan.save(update_fields=[
            'descripcion_general', 'objetivo_general', 'actividades_planeadas',
            'fecha_inicio_planeada', 'fecha_fin_planeada', 'observaciones',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el plan de trabajo del proceso '{plan.proceso.titulo}' (id={plan.pk}).",
            objeto=plan,
        )
        return plan

    @staticmethod
    @transaction.atomic
    def enviar(plan_trabajo_id, ejecutor):
        plan = PlanTrabajoSelector.obtener(plan_trabajo_id)
        validar_ejecutor_autor_o_gestor_por_proceso(
            plan.proceso, ejecutor, "este plan de trabajo"
        )
        PlanTrabajoValidator.validar_envio(plan)
        plan.estado = 'ENVIADO'
        plan.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se envió a revisión el plan de trabajo del proceso '{plan.proceso.titulo}' (id={plan.pk}).",
            objeto=plan,
        )
        return plan

    @staticmethod
    @transaction.atomic
    def aprobar(plan_trabajo_id, aprobado_por_id, ejecutor):
        # Sin cambios: acción exclusiva de Tutor/Facultad/Decano.
        plan = PlanTrabajoSelector.obtener(plan_trabajo_id)
        PlanTrabajoValidator.validar_aprobacion(plan, aprobado_por_id)
        plan.estado = 'APROBADO'
        plan.aprobado_por_id = aprobado_por_id
        plan.fecha_aprobacion = timezone.now()
        plan.save(update_fields=['estado', 'aprobado_por', 'fecha_aprobacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se aprobó el plan de trabajo del proceso '{plan.proceso.titulo}' (id={plan.pk}).",
            objeto=plan,
        )
        notificar(
            usuario_id_estudiante_de_proceso(plan.proceso),
            f"Tu plan de trabajo del proceso '{plan.proceso.titulo}' fue aprobado.",
            tipo='exito',
        )
        return plan

    @staticmethod
    @transaction.atomic
    def rechazar(plan_trabajo_id, observaciones, ejecutor):
        # Sin cambios: acción exclusiva de Tutor/Facultad/Decano.
        plan = PlanTrabajoSelector.obtener(plan_trabajo_id)
        PlanTrabajoValidator.validar_rechazo(plan, observaciones)
        plan.estado = 'RECHAZADO'
        plan.observaciones = observaciones
        plan.save(update_fields=['estado', 'observaciones'])
        HistorialService.registrar(
            ejecutor,
            f"Se rechazó el plan de trabajo del proceso '{plan.proceso.titulo}' (id={plan.pk}): "
            f"{observaciones}",
            objeto=plan,
        )
        notificar(
            usuario_id_estudiante_de_proceso(plan.proceso),
            f"Tu plan de trabajo del proceso '{plan.proceso.titulo}' fue rechazado. "
            f"Motivo: {observaciones}",
            tipo='alerta',
        )
        return plan

    @staticmethod
    @transaction.atomic
    def eliminar(plan_trabajo_id, ejecutor):
        plan = PlanTrabajoSelector.obtener(plan_trabajo_id)
        validar_ejecutor_autor_o_gestor_por_proceso(
            plan.proceso, ejecutor, "este plan de trabajo"
        )
        PlanTrabajoValidator.validar_eliminacion(plan)
        plan.estado = 'ELIMINADO'
        plan.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó el plan de trabajo del proceso '{plan.proceso.titulo}' (id={plan.pk}).",
            objeto=plan,
        )
        return plan