# apps/investigacion_formativa/selectors/registro_horas_selector.py
from apps.investigacion_formativa.models import RegistroHoras


class RegistroHorasSelector:

    @staticmethod
    def listar():
        return RegistroHoras.objects.select_related('proceso').all()

    @staticmethod
    def obtener(registro_horas_id):
        return RegistroHoras.objects.select_related('proceso').get(pk=registro_horas_id)

    @staticmethod
    def obtener_por_proceso(proceso_id):
        return (
            RegistroHoras.objects
            .select_related('proceso')
            .filter(proceso_id=proceso_id)
            .first()
        )

    @staticmethod
    def existe_para_proceso(proceso_id):
        return RegistroHoras.objects.filter(proceso_id=proceso_id).exists()