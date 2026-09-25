from rest_framework.exceptions import ValidationError


class HistorialValidator:
    """
    Historial es un log de auditoría de solo escritura: una vez creado, un
    registro nunca se edita ni se borra. Por eso este validador solo expone
    validar_creacion() — a propósito no existen validar_actualizacion() ni
    validar_eliminacion(); el Service tampoco debe ofrecer esos métodos.
    """

    @staticmethod
    def validar_creacion(accion):
        HistorialValidator._validar_accion(accion)

    @staticmethod
    def _validar_accion(accion):
        if not accion or not accion.strip():
            raise ValidationError({"accion": "La descripción de la acción es obligatoria."})