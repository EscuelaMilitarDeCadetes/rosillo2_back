"""
Selector de GrupoInvestigacion.

Migrado desde: GrupoInvestigacionServicio (Thymeleaf)
    listarGruposInvestigacion() -> listar()
    buscarGrupoInvestigacion(id) -> obtener(id)
    listarGruposXUsuario(id)     -> obtener_grupo_usuario(usuario_id)

Camino de navegación para obtener_grupo_usuario:
    Usuario -> UsuarioXPersona (related_name='asignaciones', estado=True)
            -> Persona -> PersonaXGrupo -> GrupoInvestigacion

El hack original getGrupoXUsuarioOG() (if id != 15 ... else grupo_id=4 AND
rol_grupo_fk=2) se descarta por completo — confirmado en la auditoría.
"""
from apps.institucional.models import GrupoInvestigacion


class GrupoXUsuarioAmbiguoError(Exception):
    """
    Se lanza cuando un Usuario tiene más de una vinculación PersonaXGrupo
    activa con grupo distinto de null. Decisión explícita: es una
    inconsistencia de datos a corregir, no algo que deba resolverse en
    silencio devolviendo "el primero que aparezca".
    """
    pass


class GrupoInvestigacionSelector:

    @staticmethod
    def listar():
        return GrupoInvestigacion.objects.all().order_by('nombre_grupo')

    @staticmethod
    def obtener(grupo_id):
        return GrupoInvestigacion.objects.get(pk=grupo_id)

    @staticmethod
    def buscar(grupo_id):
        return GrupoInvestigacion.objects.filter(pk=grupo_id).first()

    @staticmethod
    def existe_nombre(nombre_grupo, excluir_id=None):
        qs = GrupoInvestigacion.objects.filter(nombre_grupo__iexact=nombre_grupo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def existe_sigla(sigla_grupo, excluir_id=None):
        qs = GrupoInvestigacion.objects.filter(sigla_grupo__iexact=sigla_grupo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def obtener_grupo_usuario(usuario_id):
        """
        Migración de listarGruposXUsuario(id), sin el hack id!=15.

        Devuelve el GrupoInvestigacion vinculado a la Persona actualmente
        asignada (UsuarioXPersona.estado=True) a ese Usuario, o None si no
        tiene vinculación activa con grupo.

        Cardinalidad: si una misma Persona tuviera más de una vinculación
        activa con grupo != null (técnicamente posible, sin unique
        constraint que lo impida), se lanza GrupoXUsuarioAmbiguoError —
        decisión explícita de no tolerar esa inconsistencia en silencio.
        """
        grupos = list(
            GrupoInvestigacion.objects
            .filter(
                personaxgrupo__persona__asignaciones__usuario_id=usuario_id,
                personaxgrupo__persona__asignaciones__estado=True,
                personaxgrupo__estado=True,
            )
            .distinct()
        )
        if len(grupos) > 1:
            raise GrupoXUsuarioAmbiguoError(
                f"El usuario id={usuario_id} tiene más de una vinculación "
                f"activa a un grupo de investigación ({len(grupos)} "
                f"encontradas). Esto es una inconsistencia de datos que "
                f"debe corregirse en PersonaXGrupo antes de continuar."
            )
        return grupos[0] if grupos else None