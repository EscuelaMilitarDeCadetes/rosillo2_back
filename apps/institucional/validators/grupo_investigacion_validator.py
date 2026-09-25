"""
Validador de GrupoInvestigacion.

Interfaz estándar definitiva.
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.grupo_investigacion_selector import GrupoInvestigacionSelector


class GrupoInvestigacionValidator:

    @staticmethod
    def validar_creacion(nombre_grupo, sigla_grupo, clasificacion_grupo):
        GrupoInvestigacionValidator._validar_nombre(nombre_grupo)
        GrupoInvestigacionValidator._validar_sigla(sigla_grupo)
        GrupoInvestigacionValidator._validar_clasificacion(clasificacion_grupo)
        GrupoInvestigacionValidator._validar_unicidad_nombre(nombre_grupo)
        GrupoInvestigacionValidator._validar_unicidad_sigla(sigla_grupo)

    @staticmethod
    def validar_actualizacion(grupo_id, nombre_grupo, sigla_grupo, clasificacion_grupo):
        GrupoInvestigacionValidator._validar_nombre(nombre_grupo)
        GrupoInvestigacionValidator._validar_sigla(sigla_grupo)
        GrupoInvestigacionValidator._validar_clasificacion(clasificacion_grupo)
        GrupoInvestigacionValidator._validar_unicidad_nombre(nombre_grupo, excluir_id=grupo_id)
        GrupoInvestigacionValidator._validar_unicidad_sigla(sigla_grupo, excluir_id=grupo_id)

    @staticmethod
    def _validar_nombre(nombre_grupo):
        if not nombre_grupo or not nombre_grupo.strip():
            raise ValidationError({"nombre_grupo": "El nombre del grupo es obligatorio."})
        if len(nombre_grupo) > 50:
            raise ValidationError(
                {"nombre_grupo": f"El nombre '{nombre_grupo}' supera el máximo de 50 caracteres."}
            )

    @staticmethod
    def _validar_sigla(sigla_grupo):
        if not sigla_grupo or not sigla_grupo.strip():
            raise ValidationError({"sigla_grupo": "La sigla del grupo es obligatoria."})
        if len(sigla_grupo) > 8:
            raise ValidationError(
                {"sigla_grupo": f"La sigla '{sigla_grupo}' supera el máximo de 8 caracteres."}
            )
            
    @staticmethod
    def _validar_clasificacion(clasificacion_grupo):
        if not clasificacion_grupo or not clasificacion_grupo.strip():
            raise ValidationError({"clasificacion_grupo": "La clasificación del grupo es obligatoria."})
        if len(clasificacion_grupo) > 3:
            raise ValidationError(
                {"clasificacion_grupo": f"La clasificación '{clasificacion_grupo}' supera el máximo de 3 caracteres."}
            )

    @staticmethod
    def _validar_unicidad_nombre(nombre_grupo, excluir_id=None):
        if GrupoInvestigacionSelector.existe_nombre(nombre_grupo, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_grupo": f"Ya existe un grupo de investigación con el nombre '{nombre_grupo}'."}
            )

    @staticmethod
    def _validar_unicidad_sigla(sigla_grupo, excluir_id=None):
        if GrupoInvestigacionSelector.existe_sigla(sigla_grupo, excluir_id=excluir_id):
            raise ValidationError(
                {"sigla_grupo": f"Ya existe un grupo de investigación con la sigla '{sigla_grupo}'."}
            )