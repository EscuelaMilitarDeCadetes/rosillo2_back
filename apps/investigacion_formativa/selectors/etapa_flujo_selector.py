from apps.investigacion_formativa.models import EtapaFlujo


class EtapaFlujoSelector:

    @staticmethod
    def listar():
        return (
            EtapaFlujo.objects
            .select_related('flujo', 'documento_requerido')
            .filter(activo=True)
            .order_by('flujo', 'orden')
        )

    @staticmethod
    def obtener(etapa_id):
        return EtapaFlujo.objects.get(pk=etapa_id)
    
    @staticmethod
    def existe(etapa_id):
        return EtapaFlujo.objects.filter(pk=etapa_id).exists()

    @staticmethod
    def existe_orden_en_flujo(flujo_id, orden, excluir_id=None):
        """Valida unique_together ('flujo', 'orden') antes de crear/actualizar."""
        qs = EtapaFlujo.objects.filter(flujo_id=flujo_id, orden=orden)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_por_flujo(flujo_id):
        return (
            EtapaFlujo.objects
            .select_related('documento_requerido')
            .filter(flujo_id=flujo_id, activo=True)
            .order_by('orden')
        )