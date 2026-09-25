from rest_framework.exceptions import ValidationError


class ControlCambiosValidator:

    @staticmethod
    def validar_creacion(proyecto_id, tipo_cambio, fecha_cambio, cambio_tiempo=False,
                          cambio_investigador=False, cambio_costo=False, cambio_producto=False):
        ControlCambiosValidator._validar_proyecto(proyecto_id)
        ControlCambiosValidator._validar_tipo_cambio(tipo_cambio)
        ControlCambiosValidator._validar_al_menos_una_bandera(
            cambio_tiempo, cambio_investigador, cambio_costo, cambio_producto
        )

    @staticmethod
    def validar_actualizacion_banderas(cambio_tiempo, cambio_investigador, cambio_costo, cambio_producto):
        """El registro es append-only salvo por estas 4 banderas booleanas."""
        ControlCambiosValidator._validar_al_menos_una_bandera(
            cambio_tiempo, cambio_investigador, cambio_costo, cambio_producto
        )

    @staticmethod
    def _validar_proyecto(proyecto_id):
        if not proyecto_id:
            raise ValidationError({"proyecto": "El proyecto es obligatorio."})

    @staticmethod
    def _validar_tipo_cambio(tipo_cambio):
        if not tipo_cambio or not tipo_cambio.strip():
            raise ValidationError({"tipo_cambio": "El tipo de cambio es obligatorio."})
        if len(tipo_cambio) > 255:
            raise ValidationError(
                {"tipo_cambio": "El tipo de cambio supera el máximo de 255 caracteres."}
            )

    @staticmethod
    def _validar_al_menos_una_bandera(cambio_tiempo, cambio_investigador, cambio_costo, cambio_producto):
        if not any([cambio_tiempo, cambio_investigador, cambio_costo, cambio_producto]):
            raise ValidationError(
                "Debe marcar al menos uno de los tipos de cambio "
                "(tiempo, investigador, costo o producto)."
            )