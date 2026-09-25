# apps/investigacion_formativa/validators/evento_evaluativo_validator.py

from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.evento_evaluativo_selector import EventoEvaluativoSelector

LUGAR_MAX_LENGTH = 255
RESULTADO_MAX_LENGTH = 100


class EventoEvaluativoValidator:

    @staticmethod
    def validar_creacion(proceso_formativo_id, numero, es_obligatoria, fecha_sustentacion, lugar):
        EventoEvaluativoValidator._validar_numero(numero)
        EventoEvaluativoValidator._validar_es_obligatoria(es_obligatoria)
        EventoEvaluativoValidator._validar_fecha_sustentacion(fecha_sustentacion)
        EventoEvaluativoValidator._validar_lugar(lugar)
        EventoEvaluativoValidator._validar_unicidad_numero(proceso_formativo_id, numero)

    @staticmethod
    def validar_reprogramacion(evento, fecha_sustentacion, lugar):
        EventoEvaluativoValidator._validar_no_finalizado(evento)
        EventoEvaluativoValidator._validar_fecha_sustentacion(fecha_sustentacion)
        EventoEvaluativoValidator._validar_lugar(lugar)

    @staticmethod
    def validar_registro_resultado(evento, resultado, acta_sustentacion_id):
        if evento.resultado and evento.resultado != 'PENDIENTE':
            raise ValidationError(
                f"Esta sustentación ya tiene un resultado registrado: '{evento.resultado}'."
            )
        EventoEvaluativoValidator._validar_resultado(resultado)

    @staticmethod
    def validar_eliminacion(evento):
        if not evento.activo:
            raise ValidationError("Esta sustentación ya se encuentra eliminada.")
        if evento.resultado and evento.resultado != 'PENDIENTE':
            raise ValidationError(
                "No se puede eliminar una sustentación que ya tiene un resultado registrado."
            )

    @staticmethod
    def _validar_no_finalizado(evento):
        if evento.resultado and evento.resultado != 'PENDIENTE':
            raise ValidationError(
                "No se puede reprogramar una sustentación que ya tiene un resultado registrado."
            )

    @staticmethod
    def _validar_numero(numero):
        if numero is None:
            raise ValidationError({"numero": "El número de sustentación es obligatorio."})
        try:
            valor = int(numero)
        except (TypeError, ValueError):
            raise ValidationError({"numero": "El número de sustentación debe ser un entero."})
        if valor < 1:
            raise ValidationError({"numero": "El número de sustentación debe ser mayor o igual a 1."})

    @staticmethod
    def _validar_es_obligatoria(es_obligatoria):
        if not isinstance(es_obligatoria, bool):
            raise ValidationError({"es_obligatoria": "El campo 'es_obligatoria' debe ser verdadero o falso."})

    @staticmethod
    def _validar_fecha_sustentacion(fecha_sustentacion):
        if not fecha_sustentacion:
            raise ValidationError({"fecha_sustentacion": "La fecha de sustentación es obligatoria."})

    @staticmethod
    def _validar_lugar(lugar):
        if not lugar or not lugar.strip():
            raise ValidationError({"lugar": "El lugar de la sustentación es obligatorio."})
        if len(lugar) > LUGAR_MAX_LENGTH:
            raise ValidationError({"lugar": f"El lugar supera el máximo de {LUGAR_MAX_LENGTH} caracteres."})

    @staticmethod
    def _validar_resultado(resultado):
        if resultado and len(resultado) > RESULTADO_MAX_LENGTH:
            raise ValidationError(
                {"resultado": f"El resultado supera el máximo de {RESULTADO_MAX_LENGTH} caracteres."}
            )

    @staticmethod
    def _validar_unicidad_numero(proceso_formativo_id, numero, excluir_id=None):
        if EventoEvaluativoSelector.existe_numero_en_proceso(
            proceso_formativo_id, numero, excluir_id=excluir_id
        ):
            raise ValidationError(
                {"numero": f"Ya existe la sustentación número {numero} para este proceso."}
            )