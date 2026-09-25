from apps.investigacion_formativa.models import ValidacionAntiplagio


class ValidacionAntiplagioSelector:

    @staticmethod
    def listar():
        return ValidacionAntiplagio.objects.select_related('instancia_etapa', 'documento').all()

    @staticmethod
    def obtener(validacion_id):
        return (
            ValidacionAntiplagio.objects
            .select_related('instancia_etapa', 'documento')
            .get(pk=validacion_id)
        )

    @staticmethod
    def listar_por_instancia_etapa(instancia_etapa_id):
        return (
            ValidacionAntiplagio.objects
            .select_related('documento')
            .filter(instancia_etapa_id=instancia_etapa_id)
        )

    @staticmethod
    def existe_validacion(instancia_etapa_id, documento_id, excluir_id=None):
        qs = ValidacionAntiplagio.objects.filter(instancia_etapa_id=instancia_etapa_id, documento_id=documento_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()