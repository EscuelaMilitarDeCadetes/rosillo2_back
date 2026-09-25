from rest_framework.exceptions import ValidationError
from apps.investigacion_formal.selectors.investigador_x_proyecto_selector import (
    InvestigadorXProyectoSelector,
)
from apps.investigacion_formal.selectors.rol_investigador_selector import RolInvestigadorSelector


class InvestigadorXProyectoValidator:

    @staticmethod
    def validar_creacion(rol_investigador_id, proyecto_id, persona_x_grupo_id, orcid=None):
        InvestigadorXProyectoValidator._validar_rol_investigador(rol_investigador_id)
        InvestigadorXProyectoValidator._validar_proyecto(proyecto_id)
        InvestigadorXProyectoValidator._validar_persona_x_grupo(persona_x_grupo_id)
        InvestigadorXProyectoValidator._validar_orcid(orcid)
        existente = InvestigadorXProyectoSelector.obtener_por_combinacion(
            rol_investigador_id, proyecto_id, persona_x_grupo_id
        )
        if existente is not None and existente.estado:
            raise ValidationError(
                "Esta persona ya está registrada con este mismo rol en este proyecto."
            )

    @staticmethod
    def validar_actualizacion(investigador_x_proyecto_id, rol_investigador_id, proyecto_id,
                               persona_x_grupo_id, orcid=None):
        InvestigadorXProyectoValidator._validar_rol_investigador(rol_investigador_id)
        InvestigadorXProyectoValidator._validar_proyecto(proyecto_id)
        InvestigadorXProyectoValidator._validar_persona_x_grupo(persona_x_grupo_id)
        InvestigadorXProyectoValidator._validar_orcid(orcid)

    @staticmethod
    def validar_desvinculacion(investigador_x_proyecto):
        if not investigador_x_proyecto.estado:
            raise ValidationError("Este investigador ya fue retirado del proyecto.")

    @staticmethod
    def _validar_rol_investigador(rol_investigador_id):
        if not rol_investigador_id:
            raise ValidationError({"rol_investigador": "El rol del investigador es obligatorio."})
        if not RolInvestigadorSelector.existe(rol_investigador_id):
            raise ValidationError(
                {"rol_investigador": f"No existe un RolInvestigador con id={rol_investigador_id}."}
            )

    @staticmethod
    def _validar_proyecto(proyecto_id):
        if not proyecto_id:
            raise ValidationError({"proyecto": "El proyecto es obligatorio."})

    @staticmethod
    def _validar_persona_x_grupo(persona_x_grupo_id):
        if not persona_x_grupo_id:
            raise ValidationError(
                {"persona_x_grupo": "La vinculación institucional del investigador es obligatoria."}
            )

    @staticmethod
    def _validar_orcid(orcid):
        if orcid is not None and len(orcid) > 255:
            raise ValidationError({"orcid": "El ORCID supera el máximo de 255 caracteres."})