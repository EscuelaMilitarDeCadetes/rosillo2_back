"""
Service de FacultadXGrupo.

Interfaz: listar(), obtener(id), crear(...), actualizar(id, ...),
obtener_grupo_de_facultad(facultad_id). NO existe eliminar() — tabla
estructural permanente (mismo criterio que FacultadEscuela/GrupoInvestigacion).
"""
from django.db import transaction

from apps.common.services.historial_service import HistorialService
from apps.institucional.models import FacultadXGrupo
from apps.institucional.selectors.facultad_x_grupo_selector import FacultadXGrupoSelector
from apps.institucional.validators.facultad_x_grupo_validator import FacultadXGrupoValidator


class FacultadXGrupoService:

    @staticmethod
    def listar():
        return FacultadXGrupoSelector.listar()

    @staticmethod
    def obtener(facultad_x_grupo_id):
        return FacultadXGrupoSelector.obtener(facultad_x_grupo_id)

    @staticmethod
    @transaction.atomic
    def crear(grupo_id, facultad_id, ejecutor):
        # Import local para evitar ciclos entre services (mismo patrón que los validators)
        from apps.institucional.services.facultad_escuela_service import FacultadEscuelaService
        from apps.institucional.services.grupo_investigacion_service import GrupoInvestigacionService
        FacultadXGrupoValidator.validar_creacion(grupo_id, facultad_id)
        facultad = FacultadEscuelaService.obtener(facultad_id)
        grupo = GrupoInvestigacionService.obtener(grupo_id)
        relacion = FacultadXGrupo.objects.create(grupo_id=grupo_id, facultad_id=facultad_id)
        HistorialService.registrar(
            ejecutor,
            f"Se registró la relación entre la facultad '{facultad.abreviatura}' "
            f"y el grupo '{grupo.sigla_grupo}'",
            objeto=relacion,
        )
        return relacion

    @staticmethod
    @transaction.atomic
    def actualizar(facultad_x_grupo_id, grupo_id, facultad_id, ejecutor):
        from apps.institucional.services.facultad_escuela_service import FacultadEscuelaService
        from apps.institucional.services.grupo_investigacion_service import GrupoInvestigacionService
        relacion = FacultadXGrupoSelector.obtener(facultad_x_grupo_id)
        FacultadXGrupoValidator.validar_actualizacion(facultad_x_grupo_id, grupo_id, facultad_id)
        relacion.grupo_id = grupo_id
        relacion.facultad_id = facultad_id
        relacion.save(update_fields=["grupo_id", "facultad_id"])
        facultad = FacultadEscuelaService.obtener(facultad_id)
        grupo = GrupoInvestigacionService.obtener(grupo_id)
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la relación entre la facultad '{facultad.abreviatura}' "
            f"y el grupo '{grupo.sigla_grupo}'",
            objeto=relacion,
        )
        return relacion

    @staticmethod
    def obtener_grupo_de_facultad(facultad_id):
        """
        Usado por PersonaXGrupoValidator para la validación dura: dado el
        id de una facultad, devuelve el grupo de investigación que le
        corresponde según la regla de negocio confirmada.
        """
        return FacultadXGrupoSelector.obtener_grupo_de_facultad(facultad_id)
    
    @staticmethod
    def obtener_facultad_de_grupo(grupo_id):
        """
        Usado por PersonaXGrupoValidator cuando se vincula directamente por
        grupo_id (sin facultad explícita): permite derivar la facultad
        correspondiente en vez de exigir que la persona ya tenga una.
        """
        return FacultadXGrupoSelector.obtener_facultad_de_grupo(grupo_id)