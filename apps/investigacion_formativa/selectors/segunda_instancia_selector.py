from apps.investigacion_formativa.models import SegundaInstancia


class SegundaInstanciaSelector:

    @staticmethod
    def listar():
        return (
            SegundaInstancia.objects
            .select_related('proceso', 'instancia_etapa', 'evaluacion', 'etapa_retorno')
            .all()
        )

    @staticmethod
    def obtener(segunda_instancia_id):
        return (
            SegundaInstancia.objects
            .select_related('proceso', 'instancia_etapa', 'evaluacion', 'etapa_retorno')
            .get(pk=segunda_instancia_id)
        )

    @staticmethod
    def existe_para_proceso(proceso_id):
        return SegundaInstancia.objects.filter(proceso_id=proceso_id).exists()

    @staticmethod
    def listar_activadas_pendientes():
        """Activadas, aún no consumidas: casos que requieren seguimiento."""
        return (
            SegundaInstancia.objects
            .select_related('proceso', 'instancia_etapa')
            .filter(activada=True, consumida=False, activa=True)
        )