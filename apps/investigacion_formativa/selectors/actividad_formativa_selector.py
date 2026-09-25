from apps.investigacion_formativa.models import ActividadFormativa


class ActividadFormativaSelector:

    @staticmethod
    def listar():
        return (
            ActividadFormativa.objects
            .exclude(estado='ELIMINADA')
            .select_related('proceso_formativo', 'responsable', 'documento_soporte')
            .order_by('-fecha_inicio')
        )

    @staticmethod
    def obtener(actividad_id):
        return ActividadFormativa.objects.get(pk=actividad_id)

    @staticmethod
    def listar_por_proceso(proceso_formativo_id):
        return (
            ActividadFormativa.objects
            .select_related('responsable', 'documento_soporte')
            .filter(proceso_formativo_id=proceso_formativo_id)
            .order_by('-fecha_inicio')
        )

    @staticmethod
    def listar_por_responsable(responsable_id):
        return (
            ActividadFormativa.objects
            .select_related('proceso_formativo')
            .filter(responsable_id=responsable_id)
            .order_by('-fecha_inicio')
        )