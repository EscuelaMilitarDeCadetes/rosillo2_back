from apps.investigacion_formativa.models import InstanciaEtapa


class InstanciaEtapaSelector:

    @staticmethod
    def listar():
        return (
            InstanciaEtapa.objects
            .select_related('proceso', 'etapa')
            .order_by('proceso', 'etapa__orden')
        )

    @staticmethod
    def obtener(instancia_id):
        return InstanciaEtapa.objects.get(pk=instancia_id)
    
    @staticmethod
    def existe(instancia_id):
        return InstanciaEtapa.objects.filter(pk=instancia_id).exists()

    @staticmethod
    def existe_etapa_en_proceso(proceso_id, etapa_id, excluir_id=None):
        """Valida unique_together ('proceso', 'etapa') antes de crear/actualizar."""
        qs = InstanciaEtapa.objects.filter(proceso_id=proceso_id, etapa_id=etapa_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_por_proceso(proceso_id):
        return (
            InstanciaEtapa.objects
            .select_related('etapa')
            .filter(proceso_id=proceso_id)
            .order_by('etapa__orden')
        )