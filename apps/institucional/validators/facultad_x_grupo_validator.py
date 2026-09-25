"""
Validador de FacultadXGrupo.

Tabla estructural (igual criterio que FacultadEscuela/GrupoInvestigacion):
no se expone eliminación. Sí se permite crear/actualizar para cuando se
agreguen nuevas facultades o grupos a futuro.
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.facultad_x_grupo_selector import FacultadXGrupoSelector
from apps.institucional.selectors.facultad_escuela_selector import FacultadEscuelaSelector
from apps.institucional.selectors.grupo_investigacion_selector import GrupoInvestigacionSelector


class FacultadXGrupoValidator:

    @staticmethod
    def validar_creacion(grupo_id, facultad_id):
        FacultadXGrupoValidator._validar_existencia(grupo_id, facultad_id)
        FacultadXGrupoValidator._validar_unicidad(grupo_id, facultad_id)

    @staticmethod
    def validar_actualizacion(facultad_x_grupo_id, grupo_id, facultad_id):
        FacultadXGrupoValidator._validar_existencia(grupo_id, facultad_id)
        FacultadXGrupoValidator._validar_unicidad(grupo_id, facultad_id, excluir_id=facultad_x_grupo_id)

    @staticmethod
    def _validar_existencia(grupo_id, facultad_id):
        if not GrupoInvestigacionSelector.buscar(grupo_id):
            raise ValidationError({"grupo": f"No existe un GrupoInvestigacion con id={grupo_id}."})
        if not FacultadEscuelaSelector.buscar(facultad_id):
            raise ValidationError({"facultad": f"No existe una FacultadEscuela con id={facultad_id}."})

    @staticmethod
    def _validar_unicidad(grupo_id, facultad_id, excluir_id=None):
        if FacultadXGrupoSelector.existe_relacion(grupo_id, facultad_id, excluir_id=excluir_id):
            raise ValidationError(
                "Ya existe una asociación entre este grupo de investigación "
                "y esta facultad."
            )