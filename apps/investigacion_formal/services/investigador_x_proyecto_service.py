from django.db import transaction

from apps.investigacion_formal.models import InvestigadorXProyecto
from apps.investigacion_formal.selectors.investigador_x_proyecto_selector import (
    InvestigadorXProyectoSelector,
)
from apps.investigacion_formal.services.proyecto_setup_service import ProyectoSetupService
from apps.investigacion_formal.validators.investigador_x_proyecto_validator import (
    InvestigadorXProyectoValidator,
)
from apps.common.services.historial_service import HistorialService


class InvestigadorXProyectoService:

    @staticmethod
    def listar():
        return InvestigadorXProyectoSelector.listar()

    @staticmethod
    def obtener(investigador_x_proyecto_id):
        return InvestigadorXProyectoSelector.obtener(investigador_x_proyecto_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        return InvestigadorXProyectoSelector.listar_por_proyecto(
            proyecto_id, solo_activos=solo_activos
        )

    @staticmethod
    @transaction.atomic
    def crear(rol_investigador_id, proyecto_id, persona_x_grupo_id, ejecutor, orcid=None):
        InvestigadorXProyectoValidator.validar_creacion(
            rol_investigador_id, proyecto_id, persona_x_grupo_id, orcid
        )
        # Si existe un registro inactivo con esa misma combinación (la
        # persona fue retirada antes con este mismo rol), se reactiva en vez
        # de intentar crear uno nuevo que violaría la restricción de BD.
        existente = InvestigadorXProyectoSelector.obtener_por_combinacion(
            rol_investigador_id, proyecto_id, persona_x_grupo_id
        )
        if existente is not None:
            existente.orcid = orcid
            existente.estado = True
            existente.save(update_fields=['orcid', 'estado'])
            HistorialService.registrar(
                ejecutor,
                f"Se reincorporó a '{existente.persona_x_grupo.persona.nombre} "
                f"{existente.persona_x_grupo.persona.apellido}' como "
                f"'{existente.rol_investigador.nombre_rol_investigador}' en el "
                f"proyecto '{existente.proyecto.titulo}' (id={existente.pk}).",
                objeto=existente,
            )
            return existente
        investigador = InvestigadorXProyecto.objects.create(
            rol_investigador_id=rol_investigador_id,
            proyecto_id=proyecto_id,
            persona_x_grupo_id=persona_x_grupo_id,
            orcid=orcid,
            estado=True,
        )
        ProyectoSetupService.verificar_configuracion_completa(proyecto_id, ejecutor=ejecutor)
        HistorialService.registrar(
            ejecutor,
            f"Se vinculó a '{investigador.persona_x_grupo.persona.nombre} "
            f"{investigador.persona_x_grupo.persona.apellido}' como "
            f"'{investigador.rol_investigador.nombre_rol_investigador}' en el "
            f"proyecto '{investigador.proyecto.titulo}' (id={investigador.pk}).",
            objeto=investigador,
        )
        return investigador

    @staticmethod
    @transaction.atomic
    def actualizar(investigador_x_proyecto_id, ejecutor, rol_investigador_id=None, orcid=None):
        """Solo CINTERNO/CEXTERNO editan vinculaciones existentes."""
        investigador = InvestigadorXProyectoSelector.obtener(investigador_x_proyecto_id)

        nuevo_rol_id = (
            rol_investigador_id if rol_investigador_id is not None else investigador.rol_investigador_id
        )
        nuevo_orcid = orcid if orcid is not None else investigador.orcid

        InvestigadorXProyectoValidator.validar_actualizacion(
            investigador_x_proyecto_id,
            nuevo_rol_id,
            investigador.proyecto_id,
            investigador.persona_x_grupo_id,
            nuevo_orcid,
        )

        investigador.rol_investigador_id = nuevo_rol_id
        investigador.orcid = nuevo_orcid
        investigador.save(update_fields=['rol_investigador', 'orcid'])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la vinculación de "
            f"'{investigador.persona_x_grupo.persona.nombre} "
            f"{investigador.persona_x_grupo.persona.apellido}' en el proyecto "
            f"'{investigador.proyecto.titulo}' (id={investigador.pk}).",
            objeto=investigador,
        )
        return investigador

    @staticmethod
    @transaction.atomic
    def eliminar(investigador_x_proyecto_id, ejecutor):
        """Soft-delete; realizado por CINTERNO/CEXTERNO."""
        investigador = InvestigadorXProyectoSelector.obtener(investigador_x_proyecto_id)
        InvestigadorXProyectoValidator.validar_desvinculacion(investigador)

        investigador.estado = False
        investigador.save(update_fields=['estado'])

        HistorialService.registrar(
            ejecutor,
            f"Se retiró a "
            f"'{investigador.persona_x_grupo.persona.nombre} "
            f"{investigador.persona_x_grupo.persona.apellido}' del proyecto "
            f"'{investigador.proyecto.titulo}' (id={investigador.pk}).",
            objeto=investigador,
        )
        return investigador