"""
Service de PersonaXGrupo.

Interfaz: listar(), obtener(id), crear(...), actualizar(id, ...),
eliminar(id) [SOFT-DELETE = desvincular]. Métodos especializados:
listar_con_grupo(), listar_por_persona().

Migrado desde: PersonaXGrupoServicio (Thymeleaf)
    getAllStatusTrue() -> listar()
    mostrarTodasPersonasConGrupo() -> listar_con_grupo()
    asignarInvestigadorAGrupo() -> crear() (con grupo poblado)
    deletePersona(id)/activarPersona(id) -> eliminar(id)/reactivar(id)
        (ya NO basados en getByFkPersona(id) — operan sobre el id de
        PersonaXGrupo directamente, resolviendo la ambigüedad de "qué
        fila desactivar" que tenía el original cuando una persona podía
        tener más de una fila activa).

Todas las operaciones de escritura registran en Historial.
"""
from django.db import transaction
from django.utils import timezone

from apps.institucional.models import PersonaXGrupo
from apps.institucional.selectors.persona_x_grupo_selector import PersonaXGrupoSelector
from apps.institucional.selectors.grupo_investigacion_selector import GrupoInvestigacionSelector
from apps.institucional.selectors.facultad_escuela_selector import FacultadEscuelaSelector
from apps.institucional.selectors.rol_grupo_selector import RolGrupoSelector
from apps.institucional.validators.persona_x_grupo_validator import PersonaXGrupoValidator
from apps.common.services.historial_service import HistorialService


class PersonaXGrupoService:

    @staticmethod
    def listar():
        return PersonaXGrupoSelector.listar()

    @staticmethod
    def obtener(persona_x_grupo_id):
        return PersonaXGrupoSelector.obtener(persona_x_grupo_id)

    @staticmethod
    @transaction.atomic
    def crear(persona_id, rol_grupo_id, ejecutor, grupo_id=None, facultad_id=None,
            vinculacion=None, derivar_facultad_de_grupo=False):
        vinculacion = vinculacion or timezone.now().date()
        facultad_id_final = PersonaXGrupoValidator.validar_creacion(
            persona_id, rol_grupo_id, grupo_id, facultad_id, vinculacion,
            derivar_facultad_de_grupo=derivar_facultad_de_grupo,
        )
        vinculo = PersonaXGrupo.objects.create(
            persona_id=persona_id,
            rol_grupo_id=rol_grupo_id,
            grupo_id=grupo_id,
            facultad_id=facultad_id_final,   # <-- antes: facultad_id
            vinculacion=vinculacion,
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se vinculó a '{vinculo.persona}' como '{vinculo.rol_grupo}' "
            f"(grupo={vinculo.grupo or '—'}, facultad={vinculo.facultad or '—'}, "
            f"id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def actualizar(persona_x_grupo_id, ejecutor, rol_grupo_id=None, grupo_id=None,
                    facultad_id=None, vinculacion=None):
        vinculo = PersonaXGrupoSelector.obtener(persona_x_grupo_id)
        nuevo_rol_grupo_id = rol_grupo_id if rol_grupo_id is not None else vinculo.rol_grupo_id
        nuevo_grupo_id = grupo_id if grupo_id is not None else vinculo.grupo_id
        nueva_facultad_id = facultad_id if facultad_id is not None else vinculo.facultad_id
        nueva_vinculacion = vinculacion if vinculacion is not None else vinculo.vinculacion
        facultad_id_final = PersonaXGrupoValidator.validar_actualizacion(
            persona_x_grupo_id, vinculo.persona_id, nuevo_rol_grupo_id,
            nuevo_grupo_id, nueva_facultad_id, nueva_vinculacion,
        )
        vinculo.rol_grupo_id = nuevo_rol_grupo_id
        vinculo.grupo_id = nuevo_grupo_id
        vinculo.facultad_id = facultad_id_final
        vinculo.vinculacion = nueva_vinculacion
        vinculo.save(update_fields=["rol_grupo", "grupo", "facultad", "vinculacion"])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la vinculación de '{vinculo.persona}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo
    
    @staticmethod
    @transaction.atomic
    def trasladar_a_grupo(persona_x_grupo_id, nuevo_grupo_id, ejecutor):
        """
        Traslada una vinculación de tipo 'grupo' de un GrupoInvestigacion a otro,
        conservando persona, rol_grupo y vinculacion. Pensado para investigadores
        (roles GRUPO, CINTERNO, CEXTERNO, ASESOR), no para vinculaciones de facultad.
        """
        vinculo = PersonaXGrupoSelector.obtener(persona_x_grupo_id)

        if vinculo.grupo_id is None:
            raise ValueError(
                f"La vinculación id={persona_x_grupo_id} no es de tipo 'grupo' "
                f"(grupo actual es nulo). Use trasladar_a_facultad() si corresponde."
            )

        nuevo_grupo = GrupoInvestigacionSelector.buscar(nuevo_grupo_id)
        if nuevo_grupo is None:
            raise ValueError(f"No existe un GrupoInvestigacion con id={nuevo_grupo_id}.")

        grupo_anterior = vinculo.grupo

        PersonaXGrupoValidator.validar_actualizacion(
            persona_x_grupo_id, vinculo.persona_id, vinculo.rol_grupo_id,
            nuevo_grupo_id, vinculo.facultad_id, vinculo.vinculacion,
        )

        vinculo.grupo_id = nuevo_grupo_id
        vinculo.save(update_fields=["grupo"])

        HistorialService.registrar(
            ejecutor,
            f"Se trasladó a '{vinculo.persona}' del grupo "
            f"'{grupo_anterior}' al grupo '{nuevo_grupo}' "
            f"(vinculación id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def trasladar_a_facultad(persona_x_grupo_id, nueva_facultad_id, ejecutor):
        """
        Traslada una vinculación de tipo 'facultad' de una FacultadEscuela a otra,
        conservando persona, rol_grupo y vinculacion. Pensado para roles con
        facultad (DECANO, FACULTAD, ESTUDIANTE, JURADO, TUTOR).
        """
        vinculo = PersonaXGrupoSelector.obtener(persona_x_grupo_id)

        if vinculo.facultad_id is None:
            raise ValueError(
                f"La vinculación id={persona_x_grupo_id} no es de tipo 'facultad' "
                f"(facultad actual es nula). Use trasladar_a_grupo() si corresponde."
            )

        nueva_facultad = FacultadEscuelaSelector.buscar(nueva_facultad_id)
        if nueva_facultad is None:
            raise ValueError(f"No existe una FacultadEscuela con id={nueva_facultad_id}.")

        facultad_anterior = vinculo.facultad

        PersonaXGrupoValidator.validar_actualizacion(
            persona_x_grupo_id, vinculo.persona_id, vinculo.rol_grupo_id,
            vinculo.grupo_id, nueva_facultad_id, vinculo.vinculacion,
        )

        vinculo.facultad_id = nueva_facultad_id
        vinculo.save(update_fields=["facultad"])

        HistorialService.registrar(
            ejecutor,
            f"Se trasladó a '{vinculo.persona}' de la facultad "
            f"'{facultad_anterior}' a la facultad '{nueva_facultad}' "
            f"(vinculación id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo
    
    @staticmethod
    @transaction.atomic
    def cambiar_rol(persona_x_grupo_id, nuevo_rol_grupo_id, ejecutor):
        """
        Cambia únicamente el RolGrupo de una vinculación existente, conservando
        persona, grupo/facultad y vinculacion.
        """
        vinculo = PersonaXGrupoSelector.obtener(persona_x_grupo_id)

        nuevo_rol = RolGrupoSelector.buscar(nuevo_rol_grupo_id)
        if nuevo_rol is None:
            raise ValueError(f"No existe un RolGrupo con id={nuevo_rol_grupo_id}.")

        rol_anterior = vinculo.rol_grupo

        PersonaXGrupoValidator.validar_actualizacion(
            persona_x_grupo_id, vinculo.persona_id, nuevo_rol_grupo_id,
            vinculo.grupo_id, vinculo.facultad_id, vinculo.vinculacion,
        )

        vinculo.rol_grupo_id = nuevo_rol_grupo_id
        vinculo.save(update_fields=["rol_grupo"])

        HistorialService.registrar(
            ejecutor,
            f"Se cambió el rol de '{vinculo.persona}' de "
            f"'{rol_anterior}' a '{nuevo_rol}' "
            f"(vinculación id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def eliminar(persona_x_grupo_id, ejecutor, desvinculacion=None):
        """
        SOFT-DELETE = desvinculación. Pone estado=False y registra
        desvinculacion (fecha real de retiro). Opera sobre el id de
        PersonaXGrupo, nunca sobre el id de Persona — resuelve la
        ambigüedad que tenía el original cuando una persona podía tener
        más de una fila activa simultáneamente.
        """
        vinculo = PersonaXGrupoSelector.obtener(persona_x_grupo_id)
        desvinculacion = desvinculacion or timezone.now().date()
        PersonaXGrupoValidator.validar_desvinculacion(vinculo, desvinculacion)
        vinculo.estado = False
        vinculo.desvinculacion = desvinculacion
        vinculo.save(update_fields=["estado", "desvinculacion"])
        HistorialService.registrar(
            ejecutor,
            f"Se desvinculó a '{vinculo.persona}' de su rol "
            f"'{vinculo.rol_grupo}' (id={vinculo.pk}), con fecha de "
            f"desvinculación {desvinculacion}.",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def reactivar(persona_x_grupo_id, ejecutor):
        """
        Reactiva una vinculación previamente desvinculada. Limpia
        desvinculacion y vuelve a poner estado=True.
        """
        vinculo = PersonaXGrupoSelector.obtener(persona_x_grupo_id)
        vinculo.estado = True
        vinculo.desvinculacion = None
        vinculo.save(update_fields=["estado", "desvinculacion"])
        HistorialService.registrar(
            ejecutor,
            f"Se reactivó la vinculación de '{vinculo.persona}' como "
            f"'{vinculo.rol_grupo}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    def listar_con_grupo(excluir_rol_grupo_id=None):
        return PersonaXGrupoSelector.listar_con_grupo(excluir_rol_grupo_id=excluir_rol_grupo_id)

    @staticmethod
    def listar_por_persona(persona_id, solo_activos=True):
        return PersonaXGrupoSelector.listar_por_persona(persona_id, solo_activos=solo_activos)

    @staticmethod
    def buscar(pk):
        return PersonaXGrupoSelector.buscar(pk)

    @staticmethod
    def historial_persona(persona_id):
        return PersonaXGrupoSelector.historial_persona(persona_id)

    @staticmethod
    def listar_activas_persona(persona_id):
        return PersonaXGrupoSelector.listar_persona_activa(persona_id)

    @staticmethod
    def obtener_facultad_activa(persona_id):
        return PersonaXGrupoSelector.obtener_facultad_activa_de_persona(persona_id)

    @staticmethod
    def obtener_grupo_activo(persona_id):
        """
        Devuelve el GrupoInvestigacion activo de la Persona, o None.
        """
        fila = (
            PersonaXGrupoSelector.listar_persona_activa(persona_id)
            .filter(grupo__isnull=False)
            .select_related('grupo')
            .first()
        )
        return fila.grupo if fila else None

    @staticmethod
    def es_administrativo(persona_id):
        """
        True si la Persona tiene exactamente una vinculación activa con
        grupo=None y facultad=None (tipo admin puro).
        """
        return PersonaXGrupo.objects.filter(
            persona_id=persona_id,
            estado=True,
            grupo__isnull=True,
            facultad__isnull=True,
        ).exists()

    @staticmethod
    def pertenece_a_grupo(persona_id):
        """True si la Persona tiene alguna vinculación activa con grupo."""
        return PersonaXGrupoSelector.existe_grupo_activo(persona_id)