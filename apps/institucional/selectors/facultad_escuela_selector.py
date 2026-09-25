"""
Selector de FacultadEscuela.

Metodos existentes
    listarFacultadEscuela()          -> listar()
    listarFacultadesXUsuario(id)     -> obtener_facultad_usuario(usuario_id)
    listarFacultadesEscuelaGrupoCM() -> listar_facultades_grupo(grupo_id)

El original siempre filtraba implícitamente por el grupo CM (grupo_id=3 
hardcodeado, sin recibir parámetros). Aquí, en cambio, pero TAMPOCO existe un
valor por defecto: grupo_id es obligatorio y se valida explícitamente
más abajo. Si un caller necesita replicar el filtro CM del original,
debe pasar su id de grupo actual de forma explícita.
"""
from apps.institucional.models import FacultadEscuela
from rest_framework.exceptions import ValidationError


class FacultadXUsuarioAmbiguoError(Exception):
    """
    Se lanza cuando un Usuario tiene más de una vinculación
    PersonaXGrupo activa con facultad distinta de null.
    """
    pass


class FacultadEscuelaSelector:

    @staticmethod
    def listar():
        return FacultadEscuela.objects.all().order_by('nombre_facultad')

    @staticmethod
    def obtener(facultad_id):
        return FacultadEscuela.objects.get(pk=facultad_id)

    @staticmethod
    def buscar(facultad_id):
        return FacultadEscuela.objects.filter(pk=facultad_id).first()

    @staticmethod
    def existe_nombre(nombre_facultad, excluir_id=None):
        qs = FacultadEscuela.objects.filter(nombre_facultad__iexact=nombre_facultad)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def existe_abreviatura(abreviatura, excluir_id=None):
        qs = FacultadEscuela.objects.filter(abreviatura__iexact=abreviatura)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_facultades_grupo(grupo_id):
        """
        El grupo_id es obligatorio: se lanza ValidationError si se omite, en vez de
        aplicar un default implícito.
        """
        if grupo_id is None:
            raise ValidationError(
                "Debe especificar el grupo."
            )
        return (
            FacultadEscuela.objects
            .filter(facultadxgrupo__grupo_id=grupo_id)
            .distinct()
            .order_by('nombre_facultad')
        )

    @staticmethod
    def obtener_facultad_usuario(usuario_id):
        """
        Migración de listarFacultadesXUsuario(id) — el método bisagra del
        original (~10 controllers lo usaban junto con
        GrupoInvestigacionSelector.obtener_grupo_usuario para distinguir
        el flujo FACULTADES vs GRUPOS).

        Camino: Usuario -> UsuarioXPersona (estado=True) -> Persona ->
        PersonaXGrupo -> FacultadEscuela.

        Cardinalidad: mismo criterio que GrupoInvestigacion — más de una
        vinculación activa con facultad != null es una inconsistencia de
        datos, no un caso a resolver en silencio.
        """
        facultades = list(
            FacultadEscuela.objects
            .filter(
                personaxgrupo__persona__asignaciones__usuario_id=usuario_id,
                personaxgrupo__persona__asignaciones__estado=True,
                personaxgrupo__estado=True,
            )
            .distinct()
        )
        if len(facultades) > 1:
            raise FacultadXUsuarioAmbiguoError(
                f"El usuario id={usuario_id} tiene más de una vinculación "
                f"activa a una facultad ({len(facultades)} encontradas). "
                f"Esto es una inconsistencia de datos que debe corregirse "
                f"en PersonaXGrupo antes de continuar."
            )
        return facultades[0] if facultades else None