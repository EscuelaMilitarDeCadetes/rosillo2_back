# apps/investigacion_formal/selectors/avance_selector.py
from apps.investigacion_formal.models import Objetivos, ObjetivoXPunto


class AvanceSelector:

    @staticmethod
    def listar_objetivos_con_puntos_activos(proyecto_id):
        """Objetivos del proyecto que tienen al menos un ObjetivoXPunto activo."""
        return (
            Objetivos.objects
            .filter(proyecto_id=proyecto_id, estado=True)
            .prefetch_related('objetivoxpunto_set')
        )

    @staticmethod
    def listar_puntos_activos_por_objetivo(objetivo_id):
        return (
            ObjetivoXPunto.objects
            .select_related('punto_control')
            .filter(objetivo_id=objetivo_id, estado=True)
        )