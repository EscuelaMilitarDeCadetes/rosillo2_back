# apps/investigacion_formativa/selectors/registro_actividades_selector.py
from apps.investigacion_formativa.models import RegistroActividades


class RegistroActividadesSelector:
    @staticmethod
    def listar():
        return (
            RegistroActividades.objects
            .select_related('proceso', 'registrado_por', 'documento')
            .filter(activo=True)
        )

    @staticmethod
    def obtener(registro_id):
        return (
            RegistroActividades.objects
            .select_related('proceso', 'registrado_por', 'documento')
            .get(pk=registro_id)
        )

    @staticmethod
    def listar_por_proceso(proceso_id):
        return (
            RegistroActividades.objects
            .select_related('registrado_por', 'documento')
            .filter(proceso_id=proceso_id, activo=True)
            .order_by('-fecha_periodo')
        )

    @staticmethod
    def existe_registro(proceso_id, registrado_por_id, fecha_periodo, excluir_id=None):
        qs = RegistroActividades.objects.filter(
            proceso_id=proceso_id,
            registrado_por_id=registrado_por_id,
            fecha_periodo=fecha_periodo,
            activo=True,
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()