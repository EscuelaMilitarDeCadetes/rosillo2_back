# apps/investigacion_formativa/selectors/avance_selector.py
from apps.investigacion_formativa.models import (
    RegistroActividades, RegistroHoras, InstanciaEtapa,
)


class AvanceSelector:

    @staticmethod
    def obtener_ultimo_registro(proceso_id):
        return (
            RegistroActividades.objects
            .filter(proceso_id=proceso_id)
            .order_by('-fecha_periodo')
            .first()
        )

    @staticmethod
    def obtener_control_horas(proceso_id):
        return RegistroHoras.objects.filter(proceso_id=proceso_id).first()

    @staticmethod
    def obtener_instancia_actual(proceso_id):
        """Primera etapa del proceso que aún no ha sido aprobada (etapa vigente)."""
        return (
            InstanciaEtapa.objects
            .select_related('etapa')
            .filter(proceso_id=proceso_id)
            .exclude(estado='APROBADO')
            .order_by('etapa__orden')
            .first()
        )

    @staticmethod
    def contar_etapas_aprobadas(proceso_id):
        return InstanciaEtapa.objects.filter(proceso_id=proceso_id, estado='APROBADO').count()

    @staticmethod
    def contar_etapas_totales(proceso_id):
        return InstanciaEtapa.objects.filter(proceso_id=proceso_id).count()

    @staticmethod
    def existe_etapa_en_segunda_instancia(proceso_id):
        return InstanciaEtapa.objects.filter(
            proceso_id=proceso_id, estado='SEGUNDA_INSTANCIA'
        ).exists()