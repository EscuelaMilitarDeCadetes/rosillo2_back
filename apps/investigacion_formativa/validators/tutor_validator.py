# apps/investigacion_formativa/validators/tutor_validator.py
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.tutor_selector import TutorSelector


class TutorValidator:

    @staticmethod
    def validar_creacion(persona_id, facultad_id):
        TutorValidator._validar_persona(persona_id)
        TutorValidator._validar_facultad(facultad_id)
        TutorValidator._validar_unicidad(persona_id, facultad_id)

    @staticmethod
    def validar_actualizacion(tutor, facultad_id):
        """La persona no se reasigna (identidad del OneToOne); solo la facultad."""
        TutorValidator._validar_facultad(facultad_id)
        TutorValidator._validar_unicidad(tutor.persona_id, facultad_id, excluir_id=tutor.pk)

    @staticmethod
    def validar_activacion(tutor):
        if tutor.estado:
            raise ValidationError("Este tutor ya se encuentra activo.")

    @staticmethod
    def validar_desactivacion(tutor):
        if not tutor.estado:
            raise ValidationError("Este tutor ya se encuentra desactivado.")

    @staticmethod
    def _validar_persona(persona_id):
        if not persona_id:
            raise ValidationError({"persona": "La persona es obligatoria."})
        from apps.institucional.models import Persona

        if not Persona.objects.filter(pk=persona_id).exists():
            raise ValidationError({"persona": f"No existe una Persona con id={persona_id}."})
        if TutorSelector.existe_para_persona(persona_id):
            raise ValidationError("Esta persona ya está registrada como tutor.")

    @staticmethod
    def _validar_facultad(facultad_id):
        if not facultad_id:
            raise ValidationError({"facultad": "La facultad es obligatoria."})
        from apps.institucional.models import FacultadEscuela

        if not FacultadEscuela.objects.filter(pk=facultad_id).exists():
            raise ValidationError({"facultad": f"No existe una FacultadEscuela con id={facultad_id}."})

    @staticmethod
    def _validar_unicidad(persona_id, facultad_id, excluir_id=None):
        if TutorSelector.existe_para_persona_y_facultad(persona_id, facultad_id, excluir_id=excluir_id):
            raise ValidationError("Ya existe un tutor registrado con esta persona y esta facultad.")