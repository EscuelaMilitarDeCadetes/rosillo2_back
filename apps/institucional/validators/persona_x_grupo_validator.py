"""
Validador de PersonaXGrupo.
Implementa la validación dura confirmada explícitamente: la facultad de
una Persona determina a qué único GrupoInvestigacion puede vincularse
como investigador, según la correspondencia definida en FacultadXGrupo.
Tres tipos de vinculación válidos (confirmados explícitamente):
  1. Administrativo puro: facultad=None, grupo=None (solo rol SOPORTE
     puede crear este tipo — ese chequeo de rol vive en el ViewSet/
     permission_class, no aquí).
  2. Vinculación de facultad: facultad=<algo>, grupo=None (Decano,
     Facultad, docente, estudiante). Sin validación de correspondencia
     — es la propia fuente de verdad.
  3. Vinculación de investigador: grupo=<algo> (con o sin facultad en
     la MISMA fila). Se valida así:
       a. Si esta misma fila ya trae 'facultad' poblada, esa es la
          facultad de referencia y se persiste tal cual.
       b. Si no, se busca la facultad activa de esta Persona en otra
          fila (PersonaXGrupoSelector.obtener_facultad_activa_de_persona).
          Si la tiene, esa facultad se usa como referencia y SÍ se
          persiste en la fila (queda registrada como la facultad de la
          persona en esta vinculación de grupo).
       c. Si no tiene ninguna facultad activa y el caller lo pide
          explícitamente (derivar_facultad_de_grupo=True — caso de alta
          de investigador nuevo desde VinculacionService), se deriva una
          facultad de referencia desde FacultadXGrupo únicamente para
          validar que el grupo indicado es coherente. Esa facultad
          derivada NO se persiste: la fila queda con facultad=None,
          porque la persona en sí nunca tuvo una facultad propia.
       d. En cualquier caso, el grupo debe coincidir EXACTAMENTE con el
          grupo que FacultadXGrupo asocia a la facultad de referencia
          usada en la validación.
NO existe validar_eliminacion() en el sentido de bloqueo — PersonaXGrupo
SÍ permite soft-delete libremente (desvinculación), a diferencia de los
catálogos estructurales. El Service es quien aplica estado=False.
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.persona_x_grupo_selector import PersonaXGrupoSelector
from apps.institucional.selectors.persona_selector import PersonaSelector
from apps.institucional.selectors.rol_grupo_selector import RolGrupoSelector
from apps.institucional.selectors.grupo_investigacion_selector import GrupoInvestigacionSelector
from apps.institucional.selectors.facultad_escuela_selector import FacultadEscuelaSelector
from apps.institucional.services.facultad_x_grupo_service import FacultadXGrupoService


class PersonaXGrupoValidator:

    @staticmethod
    def validar_creacion(persona_id, rol_grupo_id, grupo_id, facultad_id, vinculacion,
                        derivar_facultad_de_grupo=False):
        PersonaXGrupoValidator._validar_persona_existe(persona_id)
        PersonaXGrupoValidator._validar_rol_grupo_existe(rol_grupo_id)
        PersonaXGrupoValidator._validar_referencias_opcionales(grupo_id, facultad_id)
        PersonaXGrupoValidator._validar_vinculacion(vinculacion)
        PersonaXGrupoValidator._validar_unicidad(persona_id, rol_grupo_id, grupo_id, facultad_id)
        facultad_final_id = facultad_id
        if grupo_id:
            facultad_final_id = PersonaXGrupoValidator._validar_correspondencia_grupo_facultad(
                persona_id, grupo_id, facultad_id,
                derivar_facultad_de_grupo=derivar_facultad_de_grupo,
            )
        return facultad_final_id

    @staticmethod
    def validar_actualizacion(persona_x_grupo_id, persona_id, rol_grupo_id, grupo_id, facultad_id, vinculacion,
                            derivar_facultad_de_grupo=False):
        PersonaXGrupoValidator._validar_persona_existe(persona_id)
        PersonaXGrupoValidator._validar_rol_grupo_existe(rol_grupo_id)
        PersonaXGrupoValidator._validar_referencias_opcionales(grupo_id, facultad_id)
        PersonaXGrupoValidator._validar_vinculacion(vinculacion)
        PersonaXGrupoValidator._validar_unicidad(
            persona_id, rol_grupo_id, grupo_id, facultad_id, excluir_id=persona_x_grupo_id
        )
        facultad_final_id = facultad_id
        if grupo_id:
            facultad_final_id = PersonaXGrupoValidator._validar_correspondencia_grupo_facultad(
                persona_id, grupo_id, facultad_id, excluir_id=persona_x_grupo_id,
                derivar_facultad_de_grupo=derivar_facultad_de_grupo,
            )
        return facultad_final_id

    @staticmethod
    def validar_desvinculacion(persona_x_grupo, desvinculacion):
        if desvinculacion is not None and desvinculacion < persona_x_grupo.vinculacion:
            raise ValidationError(
                {"desvinculacion": (
                    f"La fecha de desvinculación ({desvinculacion}) no puede "
                    f"ser anterior a la fecha de vinculación "
                    f"({persona_x_grupo.vinculacion})."
                )}
            )

    # -- Reglas atómicas ---------------------------------------------------
    @staticmethod
    def _validar_persona_existe(persona_id):
        if not persona_id:
            raise ValidationError({"persona": "La persona es obligatoria."})
        if not PersonaSelector.existe(persona_id):
            raise ValidationError({"persona": f"No existe una Persona con id={persona_id}."})

    @staticmethod
    def _validar_rol_grupo_existe(rol_grupo_id):
        if not rol_grupo_id:
            raise ValidationError({"rol_grupo": "El rol dentro del grupo/facultad es obligatorio."})
        if not RolGrupoSelector.buscar(rol_grupo_id):
            raise ValidationError({"rol_grupo": f"No existe un RolGrupo con id={rol_grupo_id}."})

    @staticmethod
    def _validar_referencias_opcionales(grupo_id, facultad_id):
        if grupo_id and not GrupoInvestigacionSelector.buscar(grupo_id):
            raise ValidationError({"grupo": f"No existe un GrupoInvestigacion con id={grupo_id}."})
        if facultad_id and not FacultadEscuelaSelector.buscar(facultad_id):
            raise ValidationError({"facultad": f"No existe una FacultadEscuela con id={facultad_id}."})

    @staticmethod
    def _validar_vinculacion(vinculacion):
        if not vinculacion:
            raise ValidationError({"vinculacion": "La fecha de vinculación es obligatoria."})

    @staticmethod
    def _validar_unicidad(persona_id, rol_grupo_id, grupo_id, facultad_id, excluir_id=None):
        if PersonaXGrupoSelector.existe_vinculacion(
            persona_id, rol_grupo_id, grupo_id, facultad_id, excluir_id=excluir_id
        ):
            raise ValidationError(
                "Ya existe exactamente esta misma combinación de persona, "
                "rol, grupo y facultad registrada."
            )

    @staticmethod
    def _validar_correspondencia_grupo_facultad(persona_id, grupo_id, facultad_id, excluir_id=None,
                                                derivar_facultad_de_grupo=False):
        """
        Determina la facultad de referencia contra la que se valida la
        correspondencia grupo-facultad (vía FacultadXGrupo) y, por
        separado, la facultad que efectivamente debe quedar persistida
        en la fila de PersonaXGrupo.

        Ambos valores coinciden salvo en un único caso: cuando la
        facultad de referencia tuvo que derivarse desde el grupo
        (derivar_facultad_de_grupo=True) porque la persona es nueva y
        no tiene ninguna facultad activa propia. En ese caso la
        derivación es solo un mecanismo de validación — no representa
        una facultad real de la persona — así que NO se persiste.
        """
        facultad_referencia_id = facultad_id
        facultad_para_guardar = facultad_id

        if not facultad_referencia_id:
            facultad_activa = PersonaXGrupoSelector.obtener_facultad_activa_de_persona(persona_id)
            if facultad_activa is not None:
                facultad_referencia_id = facultad_activa.pk
                facultad_para_guardar = facultad_activa.pk
            elif derivar_facultad_de_grupo:
                # Solo permitido cuando el caller (VinculacionService, alta de
                # investigador nuevo) lo pide explícitamente: deriva la
                # facultad desde el grupo vía FacultadXGrupo en vez de exigir
                # que la persona ya tenga una. Es puramente para validar la
                # correspondencia grupo-facultad; la persona sigue sin tener
                # facultad propia, así que facultad_para_guardar NO se toca
                # y la fila queda con facultad=None.
                facultad_derivada = FacultadXGrupoService.obtener_facultad_de_grupo(grupo_id)
                if facultad_derivada is None:
                    raise ValidationError(
                        "Esta persona no tiene ninguna vinculación de facultad "
                        "activa, y el grupo de investigación indicado tampoco "
                        "tiene ninguna facultad asociada en FacultadXGrupo. No "
                        "es posible determinar la facultad de referencia."
                    )
                facultad_referencia_id = facultad_derivada.pk
            else:
                raise ValidationError(
                    "Esta persona no tiene ninguna vinculación de facultad "
                    "activa. Toda persona debe estar vinculada primero a "
                    "una facultad antes de poder vincularse a un grupo de "
                    "investigación como investigador."
                )

        grupo_permitido = FacultadXGrupoService.obtener_grupo_de_facultad(facultad_referencia_id)
        if grupo_permitido is None:
            raise ValidationError(
                f"La facultad id={facultad_referencia_id} no tiene ningún "
                f"grupo de investigación asociado en FacultadXGrupo. No se "
                f"puede determinar a qué grupo puede vincularse esta persona."
            )

        if grupo_permitido.pk != int(grupo_id):
            raise ValidationError(
                {"grupo": (
                    f"Esta persona solo puede vincularse al grupo de "
                    f"investigación '{grupo_permitido.nombre_grupo}' "
                    f"(id={grupo_permitido.pk}), correspondiente a su "
                    f"facultad, y no al grupo id={grupo_id}."
                )}
            )

        return facultad_para_guardar