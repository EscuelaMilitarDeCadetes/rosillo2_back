from apps.investigacion_formativa.models import Revision


class RevisionSelector:

    @staticmethod
    def listar():
        return Revision.objects.select_related('instancia_etapa').all()

    @staticmethod
    def obtener(revision_id):
        return Revision.objects.select_related('instancia_etapa').get(pk=revision_id)
    
    @staticmethod
    def obtener_ultima_por_instancia_etapa(instancia_etapa_id):
        return (
            Revision.objects
            .filter(instancia_etapa_id=instancia_etapa_id)
            .order_by('-version')
            .first()
        )

    @staticmethod
    def listar_por_instancia_etapa(instancia_etapa_id):
        return (
            Revision.objects
            .filter(instancia_etapa_id=instancia_etapa_id)
            .order_by('-version')
        )

    @staticmethod
    def existe_version(instancia_etapa_id, version, excluir_id=None):
        qs = Revision.objects.filter(instancia_etapa_id=instancia_etapa_id, version=version)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()