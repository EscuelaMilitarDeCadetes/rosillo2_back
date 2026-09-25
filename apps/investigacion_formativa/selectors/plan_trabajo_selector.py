from apps.investigacion_formativa.models import PlanTrabajo


class PlanTrabajoSelector:

    @staticmethod
    def listar():
        return PlanTrabajo.objects.select_related('proceso', 'aprobado_por').all()

    @staticmethod
    def obtener(plan_trabajo_id):
        return (
            PlanTrabajo.objects
            .select_related('proceso', 'aprobado_por')
            .get(pk=plan_trabajo_id)
        )

    @staticmethod
    def obtener_por_proceso(proceso_id):
        return (
            PlanTrabajo.objects
            .select_related('aprobado_por')
            .filter(proceso_id=proceso_id)
            .first()
        )

    @staticmethod
    def existe_para_proceso(proceso_id):
        return PlanTrabajo.objects.filter(proceso_id=proceso_id).exists()