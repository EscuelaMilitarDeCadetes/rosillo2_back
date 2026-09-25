from apps.investigacion_formativa.models import TransicionFlujo


class TransicionFlujoSelector:

    @staticmethod
    def listar():
        return TransicionFlujo.objects.select_related('etapa_origen', 'etapa_destino').all()

    @staticmethod
    def obtener(transicion_id):
        return (
            TransicionFlujo.objects
            .select_related('etapa_origen', 'etapa_destino')
            .get(pk=transicion_id)
        )

    @staticmethod
    def listar_por_etapa_origen(etapa_origen_id):
        return (
            TransicionFlujo.objects
            .select_related('etapa_destino')
            .filter(etapa_origen_id=etapa_origen_id)
            .order_by('orden')
        )

    @staticmethod
    def existe_transicion(etapa_origen_id, etapa_destino_id, excluir_id=None):
        qs = TransicionFlujo.objects.filter(etapa_origen_id=etapa_origen_id, etapa_destino_id=etapa_destino_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()