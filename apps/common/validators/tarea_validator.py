from rest_framework.exceptions import ValidationError


class TareaValidator:
    @staticmethod
    def validar_creacion(asignado_a_id, descripcion, content_type_id, object_id):
        TareaValidator._validar_asignado(asignado_a_id)
        TareaValidator._validar_descripcion(descripcion)
        TareaValidator._validar_objeto_relacionado(content_type_id, object_id)

    @staticmethod
    def validar_completar(tarea):
        if tarea.completada:
            raise ValidationError("Esta tarea ya fue marcada como completada.")

    @staticmethod
    def _validar_asignado(asignado_a_id):
        if not asignado_a_id:
            raise ValidationError({"asignado_a": "El usuario asignado es obligatorio."})

    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            raise ValidationError({"descripcion": "La descripción de la tarea es obligatoria."})
        if len(descripcion) > 255:
            raise ValidationError({"descripcion": "La descripción supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_objeto_relacionado(content_type_id, object_id):
        if bool(content_type_id) != bool(object_id):
            raise ValidationError(
                "content_type y object_id deben enviarse juntos o ninguno."
            )