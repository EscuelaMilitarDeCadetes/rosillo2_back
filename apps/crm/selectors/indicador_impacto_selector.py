from apps.crm.models import IndicadorImpacto


class IndicadorImpactoSelector:

    @staticmethod
    def listar():
        return IndicadorImpacto.objects.select_related('proyecto').all()

    @staticmethod
    def obtener(indicador_id):
        return IndicadorImpacto.objects.select_related('proyecto').get(pk=indicador_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return (
            IndicadorImpacto.objects
            .filter(proyecto_id=proyecto_id)
            .order_by('kpi_nombre')
        )

    @staticmethod
    def obtener_por_proyecto_y_kpi(proyecto_id, kpi_nombre):
        return (
            IndicadorImpacto.objects
            .filter(proyecto_id=proyecto_id, kpi_nombre__iexact=kpi_nombre)
            .first()
        )

    @staticmethod
    def existe_kpi_para_proyecto(proyecto_id, kpi_nombre, excluir_id=None):
        qs = IndicadorImpacto.objects.filter(
            proyecto_id=proyecto_id, kpi_nombre__iexact=kpi_nombre
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()