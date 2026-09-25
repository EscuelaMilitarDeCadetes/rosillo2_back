# apps/investigacion_formativa/validators/regla_flujo_validator.py
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.regla_flujo_selector import ReglaFlujoSelector
from apps.investigacion_formativa.selectors.etapa_flujo_selector import EtapaFlujoSelector

TIPOS_REGLA_VALIDOS = {
    'NOTA_MINIMA', 'PORCENTAJE_ANTIPLAGIO_MAX', 'HORAS_MINIMAS', 'PROMEDIO_MINIMO',
    'PRODUCTO_CTEI_REQUERIDO', 'EVENTO_CIENTIFICO_REQUERIDO', 'TIEMPO_MAXIMO_ETAPA', 'OTRO',
}
OPERADORES_VALIDOS = {'GT', 'LT', 'EQ', 'GTE', 'LTE', 'NE'}
NOMBRE_MAX_LEN = 150
MENSAJE_ERROR_MAX_LEN = 200
ACCION_RESULTADO_MAX_LEN = 50


class ReglaFlujoValidator:

    @staticmethod
    def validar_creacion(etapa_origen_id, etapa_destino_id, nombre, operador, tipo_regla,
                          valor_minimo, valor_maximo, mensaje_error, accion_resultado,
                          descripcion, fecha_inicio, fecha_fin=None, bloqueante=False, prioridad=1):
        ReglaFlujoValidator._validar_etapa_origen(etapa_origen_id)
        ReglaFlujoValidator._validar_etapa_destino(etapa_destino_id)
        ReglaFlujoValidator._validar_nombre(nombre)
        ReglaFlujoValidator._validar_operador(operador)
        ReglaFlujoValidator._validar_tipo_regla(tipo_regla)
        ReglaFlujoValidator._validar_rango_valores(valor_minimo, valor_maximo)
        ReglaFlujoValidator._validar_mensaje_error(mensaje_error)
        ReglaFlujoValidator._validar_accion_resultado(accion_resultado)
        ReglaFlujoValidator._validar_descripcion(descripcion)
        ReglaFlujoValidator._validar_fechas(fecha_inicio, fecha_fin)
        ReglaFlujoValidator._validar_prioridad(prioridad)
        ReglaFlujoValidator._validar_unicidad(etapa_origen_id, etapa_destino_id, nombre)

    @staticmethod
    def validar_actualizacion(regla, etapa_origen_id, etapa_destino_id, nombre, operador, tipo_regla,
                               valor_minimo, valor_maximo, mensaje_error, accion_resultado,
                               descripcion, fecha_inicio, fecha_fin=None, prioridad=1):
        ReglaFlujoValidator._validar_etapa_origen(etapa_origen_id)
        ReglaFlujoValidator._validar_etapa_destino(etapa_destino_id)
        ReglaFlujoValidator._validar_nombre(nombre)
        ReglaFlujoValidator._validar_operador(operador)
        ReglaFlujoValidator._validar_tipo_regla(tipo_regla)
        ReglaFlujoValidator._validar_rango_valores(valor_minimo, valor_maximo)
        ReglaFlujoValidator._validar_mensaje_error(mensaje_error)
        ReglaFlujoValidator._validar_accion_resultado(accion_resultado)
        ReglaFlujoValidator._validar_descripcion(descripcion)
        ReglaFlujoValidator._validar_fechas(fecha_inicio, fecha_fin)
        ReglaFlujoValidator._validar_prioridad(prioridad)
        ReglaFlujoValidator._validar_unicidad(etapa_origen_id, etapa_destino_id, nombre, excluir_id=regla.pk)

    @staticmethod
    def validar_activacion(regla):
        if regla.activa:
            raise ValidationError("Esta regla ya se encuentra activa.")

    @staticmethod
    def validar_desactivacion(regla):
        """
        Única validación de baja para ReglaFlujo. 
        """
        if not regla.activa:
            raise ValidationError("Esta regla ya se encuentra desactivada.")

    @staticmethod
    def _validar_etapa_origen(etapa_origen_id):
        if not etapa_origen_id:
            raise ValidationError({"etapa_origen": "La etapa de origen es obligatoria."})
        if not EtapaFlujoSelector.existe(etapa_origen_id):
            raise ValidationError({"etapa_origen": f"No existe una EtapaFlujo con id={etapa_origen_id}."})

    @staticmethod
    def _validar_etapa_destino(etapa_destino_id):
        if not etapa_destino_id:
            raise ValidationError({"etapa_destino": "La etapa de destino es obligatoria."})
        if not EtapaFlujoSelector.existe(etapa_destino_id):
            raise ValidationError({"etapa_destino": f"No existe una EtapaFlujo con id={etapa_destino_id}."})

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre de la regla es obligatorio."})
        if len(nombre) > NOMBRE_MAX_LEN:
            raise ValidationError({"nombre": f"El nombre supera el máximo de {NOMBRE_MAX_LEN} caracteres."})

    @staticmethod
    def _validar_operador(operador):
        if not operador:
            raise ValidationError({"operador": "El operador de comparación es obligatorio."})
        if operador not in OPERADORES_VALIDOS:
            raise ValidationError(
                {"operador": f"'{operador}' no es un operador válido. Use uno de: {sorted(OPERADORES_VALIDOS)}."}
            )

    @staticmethod
    def _validar_tipo_regla(tipo_regla):
        if not tipo_regla:
            raise ValidationError({"tipo_regla": "El tipo de regla es obligatorio."})
        if tipo_regla not in TIPOS_REGLA_VALIDOS:
            raise ValidationError(
                {"tipo_regla": (
                    f"'{tipo_regla}' no es un tipo de regla válido. "
                    f"Use uno de: {sorted(TIPOS_REGLA_VALIDOS)}."
                )}
            )

    @staticmethod
    def _validar_rango_valores(valor_minimo, valor_maximo):
        if valor_minimo is None or valor_maximo is None:
            raise ValidationError("El valor mínimo y el valor máximo de la regla son obligatorios.")
        if valor_maximo < valor_minimo:
            raise ValidationError(
                {"valor_maximo": "El valor máximo no puede ser menor que el valor mínimo."}
            )

    @staticmethod
    def _validar_mensaje_error(mensaje_error):
        if not mensaje_error or not mensaje_error.strip():
            raise ValidationError({"mensaje_error": "El mensaje de error a mostrar es obligatorio."})
        if len(mensaje_error) > MENSAJE_ERROR_MAX_LEN:
            raise ValidationError(
                {"mensaje_error": f"El mensaje de error supera el máximo de {MENSAJE_ERROR_MAX_LEN} caracteres."}
            )

    @staticmethod
    def _validar_accion_resultado(accion_resultado):
        if not accion_resultado or not accion_resultado.strip():
            raise ValidationError({"accion_resultado": "La acción resultado es obligatoria."})
        if len(accion_resultado) > ACCION_RESULTADO_MAX_LEN:
            raise ValidationError(
                {"accion_resultado": f"La acción resultado supera el máximo de {ACCION_RESULTADO_MAX_LEN} caracteres."}
            )

    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            raise ValidationError({"descripcion": "La descripción de la regla es obligatoria."})

    @staticmethod
    def _validar_fechas(fecha_inicio, fecha_fin):
        if not fecha_inicio:
            raise ValidationError({"fecha_inicio": "La fecha de inicio de vigencia es obligatoria."})
        if fecha_fin is not None and fecha_fin < fecha_inicio:
            raise ValidationError(
                {"fecha_fin": "La fecha de fin de vigencia no puede ser anterior a la fecha de inicio."}
            )

    @staticmethod
    def _validar_prioridad(prioridad):
        if prioridad is None:
            raise ValidationError({"prioridad": "La prioridad es obligatoria."})
        if not isinstance(prioridad, int) or prioridad < 1:
            raise ValidationError({"prioridad": "La prioridad debe ser un entero mayor o igual a 1."})

    @staticmethod
    def _validar_unicidad(etapa_origen_id, etapa_destino_id, nombre, excluir_id=None):
        if ReglaFlujoValidator._existe_regla(etapa_origen_id, etapa_destino_id, nombre, excluir_id):
            raise ValidationError(
                "Ya existe una regla con este mismo nombre para esta transición de etapas."
            )

    @staticmethod
    def _existe_regla(etapa_origen_id, etapa_destino_id, nombre, excluir_id):
        return ReglaFlujoSelector.existe_regla(etapa_origen_id, etapa_destino_id, nombre, excluir_id=excluir_id)