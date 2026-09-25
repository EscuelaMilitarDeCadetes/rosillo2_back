from apps.investigacion_formal.models import InvestigadorXProyecto


class InvestigadorXProyectoSelector:

    @staticmethod
    def listar():
        return (
            InvestigadorXProyecto.objects
            .select_related('rol_investigador', 'proyecto', 'persona_x_grupo')
            .filter(estado=True)
        )

    @staticmethod
    def obtener(investigador_x_proyecto_id):
        return (
            InvestigadorXProyecto.objects
            .select_related('rol_investigador', 'proyecto', 'persona_x_grupo')
            .get(pk=investigador_x_proyecto_id)
        )

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        qs = (
            InvestigadorXProyecto.objects
            .select_related('rol_investigador', 'persona_x_grupo')
            .filter(proyecto_id=proyecto_id)
        )
        if solo_activos:
            qs = qs.filter(estado=True)
        return qs

    @staticmethod
    def obtener_por_combinacion(rol_investigador_id, proyecto_id, persona_x_grupo_id):
        return InvestigadorXProyecto.objects.filter(
            rol_investigador_id=rol_investigador_id,
            proyecto_id=proyecto_id,
            persona_x_grupo_id=persona_x_grupo_id,
        ).first()