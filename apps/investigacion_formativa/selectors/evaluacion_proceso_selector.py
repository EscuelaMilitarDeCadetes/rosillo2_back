from apps.investigacion_formativa.models import EvaluacionProceso


class EvaluacionProcesoSelector:

    @staticmethod
    def listar():
        return (
            EvaluacionProceso.objects
            .select_related('evaluador__persona', 'instancia_etapa__etapa', 'instancia_etapa__proceso')
            .order_by('-fecha_evaluacion')
        )

    @staticmethod
    def obtener(evaluacion_id):
        return EvaluacionProceso.objects.get(pk=evaluacion_id)
    
    @staticmethod
    def existe(evaluacion_id):
        return EvaluacionProceso.objects.filter(pk=evaluacion_id).exists()

    @staticmethod
    def existe_evaluador_en_instancia(evaluador_id, instancia_etapa_id, excluir_id=None):
        """Valida unique_together ('evaluador', 'instancia_etapa') antes de crear/actualizar."""
        qs = EvaluacionProceso.objects.filter(evaluador_id=evaluador_id, instancia_etapa_id=instancia_etapa_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_por_instancia_etapa(instancia_etapa_id):
        return (
            EvaluacionProceso.objects
            .select_related('evaluador__persona')
            .filter(instancia_etapa_id=instancia_etapa_id)
        )

    @staticmethod
    def listar_por_proceso(proceso_id):
        return (
            EvaluacionProceso.objects
            .select_related('evaluador__persona', 'instancia_etapa__etapa')
            .filter(instancia_etapa__proceso_id=proceso_id)
            .order_by('instancia_etapa__etapa__orden')
        )

    @staticmethod
    def listar_terceros_evaluadores(instancia_etapa_id=None):
        qs = EvaluacionProceso.objects.filter(es_tercer_evaluador=True)
        if instancia_etapa_id is not None:
            qs = qs.filter(instancia_etapa_id=instancia_etapa_id)
        return qs.select_related('evaluador__persona')