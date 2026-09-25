"""
Selector de FacultadXGrupo.

Tabla puente SIN precedente de Service propio en el Thymeleaf original
(FacultadXGrupoRepositorio existía pero vacío, sin queries custom — se
usaba indirectamente dentro de queries nativas de otros repos).

Es la fuente de verdad de la regla de negocio confirmada explícitamente:
un docente de una facultad solo puede investigar en el grupo que
FacultadXGrupo asocia a esa facultad. Esta tabla ya no es solo
informativa — PersonaXGrupoValidator la consulta como restricción dura.

Datos ya cargados (referencia, no se hardcodea en código):
    facultad_id=5 (EFM) -> grupo_id=0 (RENFIMIL)
    facultad_id=2 (IC)  -> grupo_id=1 (GINSI)
    facultad_id=1,3,4,6,7 -> grupo_id=2 (CM)
"""
from apps.institucional.models import FacultadXGrupo


class FacultadXGrupoSelector:

    @staticmethod
    def listar():
        return FacultadXGrupo.objects.select_related('facultad', 'grupo').all()

    @staticmethod
    def obtener(facultad_x_grupo_id):
        return FacultadXGrupo.objects.select_related('facultad', 'grupo').get(pk=facultad_x_grupo_id)

    @staticmethod
    def obtener_grupo_de_facultad(facultad_id):
        """
        Núcleo de la validación dura de PersonaXGrupo: dado el id de una
        facultad, devuelve el GrupoInvestigacion al que esa facultad está
        asociada, o None si la facultad no tiene ninguna asociación
        registrada en FacultadXGrupo (caso que no debería ocurrir según
        los datos ya cargados, pero el método no lo asume).
        """
        relacion = (
            FacultadXGrupo.objects
            .select_related('grupo')
            .filter(facultad_id=facultad_id)
            .first()
        )
        return relacion.grupo if relacion else None
    
    @staticmethod
    def obtener_facultad_de_grupo(grupo_id):
        """
        Dirección inversa de obtener_grupo_de_facultad(): dado el id de un
        GrupoInvestigacion, devuelve la FacultadEscuela a la que está
        asociado según FacultadXGrupo, o None si no tiene asociación.
        """
        relacion = (
            FacultadXGrupo.objects
            .select_related('facultad')
            .filter(grupo_id=grupo_id)
            .first()
        )
        return relacion.facultad if relacion else None

    @staticmethod
    def existe_relacion(grupo_id, facultad_id, excluir_id=None):
        qs = FacultadXGrupo.objects.filter(grupo_id=grupo_id, facultad_id=facultad_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()