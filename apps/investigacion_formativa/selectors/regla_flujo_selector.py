# apps/investigacion_formativa/selectors/regla_flujo_selector.py
from apps.investigacion_formativa.models import ReglaFlujo


class ReglaFlujoSelector:

    @staticmethod
    def listar():
        return ReglaFlujo.objects.select_related('etapa_origen', 'etapa_destino').all()

    @staticmethod
    def obtener(regla_flujo_id):
        return (
            ReglaFlujo.objects
            .select_related('etapa_origen', 'etapa_destino')
            .get(pk=regla_flujo_id)
        )

    @staticmethod
    def listar_por_transicion(etapa_origen_id, etapa_destino_id):
        return (
            ReglaFlujo.objects
            .filter(etapa_origen_id=etapa_origen_id, etapa_destino_id=etapa_destino_id)
            .order_by('prioridad')
        )

    @staticmethod
    def existe_regla(etapa_origen_id, etapa_destino_id, nombre, excluir_id=None):
        qs = ReglaFlujo.objects.filter(
            etapa_origen_id=etapa_origen_id,
            etapa_destino_id=etapa_destino_id,
            nombre__iexact=nombre,
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()