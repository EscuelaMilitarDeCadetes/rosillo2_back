# apps/investigacion_formal/services/investigador_completo_service.py
"""
Orquestador de registro de investigador nuevo (Persona + PersonaXGrupo +
InvestigadorXProyecto en una sola transacción).

Por qué existe: PersonaService.crear() y PersonaXGrupoService.crear() son
deliberadamente EsSoporte-only (ver docstring de persona_service.py: "la
creación de Usuario+Rol no pertenece a institucional... Eso es
responsabilidad de una capa orquestadora superior [...] o un endpoint
compuesto"). CINTERNO/CEXTERNO/FACULTAD/GRUPO SÍ pueden crear
InvestigadorXProyecto directamente (ROLES_CREACION_OPERATIVA), pero no
tienen forma de dar de alta una Persona nueva para vincularla — este
service cierra ese hueco, replicando newInvestigadorFull() del Thymeleaf
original, sin tocar los permisos generales de PersonaViewSet/
PersonaXGrupoViewSet (que deben seguir siendo EsSoporte-only para su uso
normal como catálogo administrado).

Réplica de investigadorXProyectoServicio.newInvestigadorFull() (Thymeleaf):
  1. Crear la Persona (grado, nombre, apellido, documento, celular, correo, cvlac).
  2. Vincularla a un Grupo de Investigación vía PersonaXGrupo (rol_grupo,
     grupo, vinculacion=hoy; facultad derivada de FacultadXGrupo).
  3. Vincular esa PersonaXGrupo al Proyecto vía InvestigadorXProyecto
     (rol_investigador).
Todo en una sola transacción atómica: si cualquier paso falla, no debe
quedar una Persona huérfana sin PersonaXGrupo ni InvestigadorXProyecto.

NO se agrega un validator propio: cada paso delega en el validator de su
propio dominio (PersonaValidator, PersonaXGrupoValidator,
InvestigadorXProyectoValidator), que ya cubren sus campos por completo —
igual que VinculacionService reutiliza PersonaService/PasswordService en
vez de reimplementar sus validaciones. Duplicar esas reglas aquí sería
puro riesgo de que las dos copias diverjan con el tiempo.
"""
from django.db import transaction

from apps.institucional.services.persona_service import PersonaService
from apps.institucional.services.persona_x_grupo_service import PersonaXGrupoService
from apps.investigacion_formal.services.investigador_x_proyecto_service import (
    InvestigadorXProyectoService,
)


class InvestigadorCompletoService:

    @staticmethod
    @transaction.atomic
    def registrar_completo(grado_id, nombre, apellido, documento, celular, correo,
                            grupo_id, rol_grupo_id, proyecto_id, rol_investigador_id,
                            ejecutor, cvlac=None, orcid=None, vinculacion=None):
        persona = PersonaService.crear(
            grado_id=grado_id,
            nombre=nombre,
            apellido=apellido,
            documento=documento,
            celular=celular,
            correo=correo,
            cvlac=cvlac,
            ejecutor=ejecutor,
        )

        # derivar_facultad_de_grupo=True: réplica exacta de
        # VinculacionService._crear_vinculacion_grupo — esta Persona es
        # nueva y nunca tuvo una facultad previa, así que la facultad de
        # referencia se deriva de FacultadXGrupo para el grupo dado.
        # vinculacion: el Thymeleaf original no pedía esta fecha en el
        # formulario (siempre quedaba en hoy); se deja opcional aquí por
        # si el frontend la envía, pero si no viene, PersonaXGrupoService
        # la default-ea a timezone.now().date() igual que antes.
        persona_x_grupo = PersonaXGrupoService.crear(
            persona_id=persona.pk,
            rol_grupo_id=rol_grupo_id,
            grupo_id=grupo_id,
            ejecutor=ejecutor,
            vinculacion=vinculacion,
            derivar_facultad_de_grupo=True,
        )

        investigador = InvestigadorXProyectoService.crear(
            rol_investigador_id=rol_investigador_id,
            proyecto_id=proyecto_id,
            persona_x_grupo_id=persona_x_grupo.pk,
            ejecutor=ejecutor,
            orcid=orcid,
        )

        return investigador