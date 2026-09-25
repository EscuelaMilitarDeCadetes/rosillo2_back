# apps/investigacion_formativa/validators/actividad_formativa_validator.py
from rest_framework.exceptions import ValidationError


class ActividadFormativaValidator:

    ESTADOS_TERMINALES = ('COMPLETADA', 'CANCELADA')

    @staticmethod
    def validar_creacion(proceso_formativo_id, responsable_id, nombre, descripcion,
                          fecha_inicio, fecha_fin, horas_dedicadas):
        ActividadFormativaValidator._validar_relaciones(proceso_formativo_id, responsable_id)
        ActividadFormativaValidator._validar_nombre(nombre)
        ActividadFormativaValidator._validar_descripcion(descripcion)
        ActividadFormativaValidator._validar_fechas(fecha_inicio, fecha_fin)
        ActividadFormativaValidator._validar_horas_dedicadas(horas_dedicadas)

    @staticmethod
    def validar_actualizacion(actividad, nombre, descripcion, fecha_inicio, fecha_fin, horas_dedicadas):
        ActividadFormativaValidator._validar_no_terminal(actividad)
        ActividadFormativaValidator._validar_nombre(nombre)
        ActividadFormativaValidator._validar_descripcion(descripcion)
        ActividadFormativaValidator._validar_fechas(fecha_inicio, fecha_fin)
        ActividadFormativaValidator._validar_horas_dedicadas(horas_dedicadas)

    @staticmethod
    def validar_inicio(actividad):
        """PLANIFICADA -> EN_PROGRESO."""
        if actividad.estado != 'PLANIFICADA':
            raise ValidationError(
                f"Solo se pueden iniciar actividades en estado 'PLANIFICADA'. Estado actual: '{actividad.estado}'."
            )

    @staticmethod
    def validar_completado(actividad, documento_soporte_id):
        """EN_PROGRESO -> COMPLETADA; exige documento soporte."""
        if actividad.estado != 'EN_PROGRESO':
            raise ValidationError(
                f"Solo se pueden completar actividades en estado 'EN_PROGRESO'. Estado actual: '{actividad.estado}'."
            )
        if documento_soporte_id is None:
            raise ValidationError(
                {"documento_soporte_id": "Debe adjuntar un documento soporte para completar la actividad."}
            )

    @staticmethod
    def validar_cancelacion(actividad):
        ActividadFormativaValidator._validar_no_terminal(actividad)

    @staticmethod
    def validar_eliminacion(actividad):
        if actividad.estado == 'ELIMINADA':
            raise ValidationError("Esta actividad ya se encuentra eliminada.")
        if actividad.estado != 'PLANIFICADA':
            raise ValidationError(
                f"Solo se pueden eliminar actividades en estado 'PLANIFICADA'. "
                f"Estado actual: '{actividad.estado}'."
            )

    @staticmethod
    def _validar_no_terminal(actividad):
        if actividad.estado in ActividadFormativaValidator.ESTADOS_TERMINALES:
            raise ValidationError(
                f"No se puede modificar una actividad en estado '{actividad.estado}'."
            )

    @staticmethod
    def _validar_relaciones(proceso_formativo_id, responsable_id):
        if not proceso_formativo_id:
            raise ValidationError({"proceso_formativo": "El proceso formativo es obligatorio."})
        if not responsable_id:
            raise ValidationError({"responsable": "El responsable de la actividad es obligatorio."})

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre de la actividad es obligatorio."})
        if len(nombre) > 255:
            raise ValidationError({"nombre": "El nombre supera el máximo de 255 caracteres."})
        
    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            return
        if len(descripcion) > 255:
            raise ValidationError({"descripcion": "La descripcion supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_fechas(fecha_inicio, fecha_fin):
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )

    @staticmethod
    def _validar_horas_dedicadas(horas_dedicadas):
        if horas_dedicadas is None:
            return
        try:
            valor = float(horas_dedicadas)
        except (TypeError, ValueError):
            raise ValidationError({"horas_dedicadas": "Las horas dedicadas deben ser numéricas."})
        if valor < 0:
            raise ValidationError({"horas_dedicadas": "Las horas dedicadas no pueden ser negativas."})