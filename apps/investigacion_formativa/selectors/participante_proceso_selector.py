# apps/investigacion_formativa/selectors/participante_proceso_selector.py
from apps.investigacion_formativa.models import ParticipanteProceso


class ParticipanteProcesoSelector:

    @staticmethod
    def listar():
        return (
            ParticipanteProceso.objects
            .select_related('proceso_formativo', 'persona')
            .all()
        )

    @staticmethod
    def obtener(participante_id):
        return (
            ParticipanteProceso.objects
            .select_related('proceso_formativo', 'persona')
            .get(pk=participante_id)
        )

    @staticmethod
    def listar_por_proceso(proceso_formativo_id):
        return (
            ParticipanteProceso.objects
            .select_related('persona')
            .filter(proceso_formativo_id=proceso_formativo_id)
        )
    
    @staticmethod
    def listar_estudiantes_por_proceso(proceso_formativo_id):
        return ParticipanteProceso.objects.select_related('persona').filter(
            proceso_formativo_id=proceso_formativo_id, rol_en_modalidad='ESTUDIANTE'
        )
    
    @staticmethod
    def listar_activos_por_proceso(proceso_formativo_id):
        return (
            ParticipanteProceso.objects
            .select_related('persona')
            .filter(proceso_formativo_id=proceso_formativo_id, activo=True)
        )
        
    @staticmethod
    def obtener_por_proceso_y_persona(proceso_formativo_id, persona_id):
        return (
            ParticipanteProceso.objects
            .filter(proceso_formativo_id=proceso_formativo_id, persona_id=persona_id)
            .first()
        )