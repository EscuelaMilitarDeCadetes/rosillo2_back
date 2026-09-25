# apps/investigacion_formativa/validators/estudiante_validator.py

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.estudiante_selector import EstudianteSelector


class EstudianteValidator:

    @staticmethod
    def validar_creacion(persona_id, correo_personal, nivel):
        EstudianteValidator._validar_correo(correo_personal)
        EstudianteValidator._validar_nivel(nivel)
        EstudianteValidator._validar_unicidad(persona_id)

    @staticmethod
    def validar_actualizacion(correo_personal, nivel):
        # El service solo actualiza correo_personal y nivel; persona/modalidad_facultad
        # no cambian en este flujo, así que no se revalida su unicidad aquí.
        EstudianteValidator._validar_correo(correo_personal)
        EstudianteValidator._validar_nivel(nivel)

    @staticmethod
    def validar_activacion(estudiante):
        if estudiante.estado:
            raise ValidationError("Este estudiante ya se encuentra activo.")

    @staticmethod
    def validar_eliminacion(estudiante):
        if not estudiante.estado:
            raise ValidationError("Este estudiante ya se encuentra desactivado.")

    @staticmethod
    def _validar_correo(correo_personal):
        if not correo_personal or not correo_personal.strip():
            raise ValidationError({"correo_personal": "El correo personal es obligatorio."})
        try:
            validate_email(correo_personal)
        except DjangoValidationError:
            raise ValidationError({"correo_personal": "El correo personal no tiene un formato válido."})

    @staticmethod
    def _validar_nivel(nivel):
        if not nivel or not nivel.strip():
            raise ValidationError({"nivel": "El nivel del estudiante es obligatorio."})
        if len(nivel) > 50:
            raise ValidationError({"nivel": "El nivel supera el máximo de 50 caracteres."})

    @staticmethod
    def _validar_unicidad(persona_id, excluir_id=None):
        if EstudianteSelector.existe_persona(persona_id, excluir_id=excluir_id):
            raise ValidationError(
                "Esta persona ya está registrada como estudiante."
            )