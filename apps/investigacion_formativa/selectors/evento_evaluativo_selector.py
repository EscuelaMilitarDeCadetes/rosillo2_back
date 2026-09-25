from django.utils import timezone

from apps.investigacion_formativa.models import EventoEvaluativo


class EventoEvaluativoSelector:

    @staticmethod
    def listar():
        return (
            EventoEvaluativo.objects
            .select_related('proceso_formativo', 'acta_sustentacion')
            .filter(activo=True)
            .order_by('-fecha_sustentacion')
        )

    @staticmethod
    def obtener(evento_id):
        return EventoEvaluativo.objects.get(pk=evento_id)

    @staticmethod
    def listar_por_proceso(proceso_formativo_id):
        return (
            EventoEvaluativo.objects
            .select_related('acta_sustentacion')
            .filter(proceso_formativo_id=proceso_formativo_id, activo=True)
            .order_by('numero')
        )

    @staticmethod
    def listar_proximas(proceso_formativo_id=None):
        qs = EventoEvaluativo.objects.filter(fecha_sustentacion__gte=timezone.now(), activo=True)
        if proceso_formativo_id is not None:
            qs = qs.filter(proceso_formativo_id=proceso_formativo_id)
        return qs.order_by('fecha_sustentacion')
    
    @staticmethod
    def existe_numero_en_proceso(proceso_formativo_id, numero, excluir_id=None):
        qs = EventoEvaluativo.objects.filter(
            proceso_formativo_id=proceso_formativo_id, numero=numero, activo=True,
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()