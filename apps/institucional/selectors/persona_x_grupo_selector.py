"""
Selector de PersonaXGrupo.

Migrado desde: PersonaXGrupoServicio (Thymeleaf)
    getAllStatusTrue() -> listar() [filtrado a estado=True, ver nota]
    mostrarTodasPersonasConGrupo() -> listar_con_grupo()

NO migrado tal cual: el filtro original 'rol_grupo_fk != 3' (excluía
ASESOR) en mostrarTodasPersonasConGrupo() se reemplaza por un parámetro
explícito en lugar de un hardcode silencioso — ver listar_con_grupo().

NO migrado: deletePersona(id)/activarPersona(id) basados en
getByFkPersona(id) (asumían 1 sola fila activa por persona — ambigüedad
real ya documentada en la auditoría). Aquí el soft-delete opera sobre el
id de PersonaXGrupo directamente, nunca sobre el id de Persona.
"""
from apps.institucional.models import PersonaXGrupo


class PersonaXGrupoSelector:

    @staticmethod
    def listar():
        """Equivalente a PersonaXGrupoServicio.getAllStatusTrue()."""
        return (
            PersonaXGrupo.objects
            .select_related('persona', 'rol_grupo', 'facultad', 'grupo')
            .filter(estado=True)
        )

    @staticmethod
    def obtener(persona_x_grupo_id):
        return (
            PersonaXGrupo.objects
            .select_related('persona', 'rol_grupo', 'facultad', 'grupo')
            .get(pk=persona_x_grupo_id)
        )

    @staticmethod
    def buscar(persona_x_grupo_id):
        return (
            PersonaXGrupo.objects
            .select_related('persona', 'rol_grupo', 'facultad', 'grupo')
            .filter(pk=persona_x_grupo_id)
            .first()
        )

    @staticmethod
    def listar_por_persona(persona_id, solo_activos=True):
        qs = (
            PersonaXGrupo.objects
            .select_related('rol_grupo', 'facultad', 'grupo')
            .filter(persona_id=persona_id)
        )
        if solo_activos:
            qs = qs.filter(estado=True)
        return qs

    @staticmethod
    def obtener_facultad_activa_de_persona(persona_id):
        """
        Núcleo de la validación dura grupo<->facultad: busca la fila
        PersonaXGrupo activa de esta Persona donde 'facultad' esté
        poblada (independientemente de si 'grupo' también lo está).
        Devuelve la FacultadEscuela, o None si la Persona no tiene
        ninguna vinculación de facultad activa.
        """
        fila = (
            PersonaXGrupo.objects
            .select_related('facultad')
            .filter(persona_id=persona_id, estado=True, facultad__isnull=False)
            .first()
        )
        return fila.facultad if fila else None

    @staticmethod
    def listar_con_grupo(excluir_rol_grupo_id=None):
        """
        Equivalente a PersonaXGrupoServicio.mostrarTodasPersonasConGrupo().

        El original excluía con un hardcode SQL "rol_grupo_fk != 3"
        (ASESOR). Aquí se recibe excluir_rol_grupo_id explícitamente en
        vez de hardcodearlo — quien llame decide si replica ese
        comportamiento pasando el id correspondiente, o lista todos sin
        exclusión si no pasa nada.
        """
        qs = (
            PersonaXGrupo.objects
            .select_related('persona', 'rol_grupo', 'grupo')
            .filter(estado=True, grupo__isnull=False)
        )
        if excluir_rol_grupo_id is not None:
            qs = qs.exclude(rol_grupo_id=excluir_rol_grupo_id)
        return qs
    
    @staticmethod
    def existe_grupo_activo(persona_id):
        return (
            PersonaXGrupo.objects
            .filter(persona_id=persona_id, grupo__isnull=False, estado=True)
            .exists()
        )

    @staticmethod
    def existe_vinculacion(persona_id, rol_grupo_id, grupo_id, facultad_id, excluir_id=None):
        """
        Soporta la unique_together del modelo
        (persona, rol_grupo, grupo, facultad).
        """
        qs = PersonaXGrupo.objects.filter(
            persona_id=persona_id,
            rol_grupo_id=rol_grupo_id,
            grupo_id=grupo_id,
            facultad_id=facultad_id,
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
    
    @staticmethod
    def listar_persona_activa(persona_id):
        return (
            PersonaXGrupo.objects
            .select_related("rol_grupo", "grupo", "facultad")
            .filter(persona_id=persona_id, estado=True,)
        )

    @staticmethod
    def historial_persona(persona_id):
        return (
            PersonaXGrupo.objects
            .select_related("rol_grupo", "grupo", "facultad")
            .filter(persona_id=persona_id)
            .order_by("-vinculacion")
        )