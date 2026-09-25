from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.grupo_minciencias_selector import GrupoMincienciasSelector


class GrupoMincienciasValidator:

    @staticmethod
    def validar_creacion(nombre_grupo_minciencias):
        GrupoMincienciasValidator._validar_nombre(nombre_grupo_minciencias)
        GrupoMincienciasValidator._validar_unicidad(nombre_grupo_minciencias)

    @staticmethod
    def validar_actualizacion(grupo_minciencias_id, nombre_grupo_minciencias):
        GrupoMincienciasValidator._validar_nombre(nombre_grupo_minciencias)
        GrupoMincienciasValidator._validar_unicidad(
            nombre_grupo_minciencias, excluir_id=grupo_minciencias_id
        )

    @staticmethod
    def _validar_nombre(nombre_grupo_minciencias):
        if not nombre_grupo_minciencias or not nombre_grupo_minciencias.strip():
            raise ValidationError(
                {"nombre_grupo_minciencias": "El nombre del grupo Minciencias es obligatorio."}
            )
        if len(nombre_grupo_minciencias) > 150:
            raise ValidationError(
                {"nombre_grupo_minciencias": "El nombre supera el máximo de 150 caracteres."}
            )

    @staticmethod
    def _validar_unicidad(nombre_grupo_minciencias, excluir_id=None):
        if GrupoMincienciasSelector.existe_nombre(nombre_grupo_minciencias, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_grupo_minciencias": f"Ya existe el grupo Minciencias '{nombre_grupo_minciencias}'."}
            )