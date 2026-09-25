# apps/investigacion_formativa/selectors/homologacion_selector.py
from apps.investigacion_formativa.models import Homologacion


class HomologacionSelector:

    @staticmethod
    def listar():
        return (
            Homologacion.objects
            .select_related('proceso', 'acta_homologacion', 'aprobado_por')
            .order_by('-fecha_homologacion')
        )

    @staticmethod
    def obtener(homologacion_id):
        return Homologacion.objects.get(pk=homologacion_id)

    @staticmethod
    def obtener_por_proceso(proceso_id):
        """El proceso tiene a lo sumo una homologación (OneToOneField)."""
        return Homologacion.objects.filter(proceso_id=proceso_id).first()

    @staticmethod
    def existe_para_proceso(proceso_id):
        return Homologacion.objects.filter(proceso_id=proceso_id).exists()

    @staticmethod
    def listar_pendientes():
        return Homologacion.objects.filter(estado='PENDIENTE').select_related('proceso')