"""
Validador de RolGrupo.

Interfaz estándar definitiva. Todos los mensajes son explícitos.
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.rol_grupo_selector import RolGrupoSelector


class RolGrupoValidator:

    @staticmethod
    def validar_creacion(cargo):
        RolGrupoValidator._validar_cargo(cargo)
        RolGrupoValidator._validar_unicidad_cargo(cargo)

    @staticmethod
    def validar_actualizacion(rol_grupo_id, cargo):
        RolGrupoValidator._validar_cargo(cargo)
        RolGrupoValidator._validar_unicidad_cargo(cargo, excluir_id=rol_grupo_id)

    @staticmethod
    def _validar_cargo(cargo):
        if not cargo or not cargo.strip():
            raise ValidationError({"cargo": "El nombre del cargo es obligatorio."})
        if len(cargo) > 50:
            raise ValidationError(
                {"cargo": f"El cargo '{cargo}' supera el máximo de 50 caracteres."}
            )

    @staticmethod
    def _validar_unicidad_cargo(cargo, excluir_id=None):
        if RolGrupoSelector.existe_cargo(cargo, excluir_id=excluir_id):
            raise ValidationError(
                {"cargo": f"Ya existe un rol de grupo con el nombre '{cargo}'."}
            )