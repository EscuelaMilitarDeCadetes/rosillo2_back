from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.rol_investigador_selector import RolInvestigadorSelector


class RolInvestigadorValidator:

    @staticmethod
    def validar_creacion(nombre_rol_investigador, descripcion):
        RolInvestigadorValidator._validar_nombre(nombre_rol_investigador)
        RolInvestigadorValidator._validar_descripcion(descripcion)
        RolInvestigadorValidator._validar_unicidad(nombre_rol_investigador)

    @staticmethod
    def validar_actualizacion(rol_investigador_id, nombre_rol_investigador, descripcion):
        RolInvestigadorValidator._validar_nombre(nombre_rol_investigador)
        RolInvestigadorValidator._validar_descripcion(descripcion)
        RolInvestigadorValidator._validar_unicidad(
            nombre_rol_investigador, excluir_id=rol_investigador_id
        )

    @staticmethod
    def _validar_nombre(nombre_rol_investigador):
        if not nombre_rol_investigador or not nombre_rol_investigador.strip():
            raise ValidationError(
                {"nombre_rol_investigador": "El nombre del rol de investigador es obligatorio."}
            )
        if len(nombre_rol_investigador) > 50:
            raise ValidationError(
                {"nombre_rol_investigador": "El nombre supera el máximo de 50 caracteres."}
            )

    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            raise ValidationError({"descripcion": "La descripción del rol es obligatoria."})
        if len(descripcion) > 150:
            raise ValidationError({"descripcion": "La descripción supera el máximo de 150 caracteres."})

    @staticmethod
    def _validar_unicidad(nombre_rol_investigador, excluir_id=None):
        if RolInvestigadorSelector.existe_nombre(nombre_rol_investigador, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_rol_investigador": f"Ya existe el rol de investigador '{nombre_rol_investigador}'."}
            )