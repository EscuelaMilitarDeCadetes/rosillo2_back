# apps/investigacion_formativa/validators/banco_ideas_validator.py

from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.banco_ideas_selector import BancoIdeasSelector


class BancoIdeasValidator:

    @staticmethod
    def validar_creacion(facultad_id, idea, descripcion, linea_investigacion, palabras_clave):
        BancoIdeasValidator._validar_idea(idea)
        BancoIdeasValidator._validar_campo_requerido(descripcion, "descripcion", "La descripción")
        BancoIdeasValidator._validar_campo_requerido(linea_investigacion, "linea_investigacion", "La línea de investigación")
        BancoIdeasValidator._validar_campo_requerido(palabras_clave, "palabras_clave", "Las palabras clave")
        BancoIdeasValidator._validar_unicidad(facultad_id, idea)

    @staticmethod
    def validar_actualizacion(banco_idea, descripcion, linea_investigacion, palabras_clave):
        BancoIdeasValidator._validar_campo_requerido(descripcion, "descripcion", "La descripción")
        BancoIdeasValidator._validar_campo_requerido(linea_investigacion, "linea_investigacion", "La línea de investigación")
        BancoIdeasValidator._validar_campo_requerido(palabras_clave, "palabras_clave", "Las palabras clave")

    @staticmethod
    def validar_separacion(banco_idea):
        """Paso previo a asignar la idea a un estudiante concreto."""
        if banco_idea.estado != 'DISPONIBLE':
            raise ValidationError(
                f"Solo se pueden separar ideas en estado 'DISPONIBLE'. Estado actual: '{banco_idea.estado}'."
            )

    @staticmethod
    def validar_toma(banco_idea):
        """Se ejecuta cuando el ProcesoFormativo asociado ya fue creado formalmente."""
        if banco_idea.estado not in ('DISPONIBLE', 'SEPARADA'):
            raise ValidationError(
                f"No se puede tomar una idea en estado '{banco_idea.estado}'."
            )

    @staticmethod
    def validar_liberacion(banco_idea):
        """Devuelve una idea SEPARADA a DISPONIBLE, ej. si el estudiante desiste."""
        if banco_idea.estado != 'SEPARADA':
            raise ValidationError(
                f"Solo se pueden liberar ideas en estado 'SEPARADA'. Estado actual: '{banco_idea.estado}'."
            )

    @staticmethod
    def validar_eliminacion(banco_idea):
        if banco_idea.estado == 'ELIMINADA':
            raise ValidationError("Esta idea ya se encuentra eliminada.")
        if banco_idea.estado == 'TOMADA':
            raise ValidationError("No se puede eliminar una idea que ya fue tomada por un estudiante.")

    @staticmethod
    def _validar_idea(idea):
        if not idea or not idea.strip():
            raise ValidationError({"idea": "El título de la idea es obligatorio."})
        if len(idea) > 255:
            raise ValidationError({"idea": "El título de la idea supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_campo_requerido(valor, campo, etiqueta):
        if not valor or not str(valor).strip():
            raise ValidationError({campo: f"{etiqueta} es obligatoria."})
        if len(str(valor)) > 255:
            raise ValidationError({campo: f"{etiqueta} supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_unicidad(facultad_id, idea, excluir_id=None):
        if BancoIdeasSelector.existe_idea_en_facultad(facultad_id, idea, excluir_id=excluir_id):
            raise ValidationError(
                {"idea": f"Ya existe una idea con el título '{idea}' registrada en esta facultad."}
            )