from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.requisito_modalidad_selector import (
    RequisitoModalidadSelector,
)
from apps.investigacion_formativa.selectors.modalidad_selector import ModalidadSelector

TIPOS_VALIDOS = {
    'PROMEDIO_MINIMO', 'HORAS_MINIMAS', 'PROYECTO_FORMAL', 'PRODUCTO_CTEI',
    'EVENTO_CIENTIFICO', 'CERTIFICADO_EXTERNO', 'OTRO',
}
TIPOS_CON_VALOR_NUMERICO = {'PROMEDIO_MINIMO', 'HORAS_MINIMAS'}
TIPOS_CON_VALOR_BOOLEANO = {'PROYECTO_FORMAL', 'PRODUCTO_CTEI', 'EVENTO_CIENTIFICO', 'CERTIFICADO_EXTERNO'}


class RequisitoModalidadValidator:

    @staticmethod
    def validar_creacion(modalidad_id, tipo, descripcion, valor_numerico=None, valor_booleano=None):
        RequisitoModalidadValidator._validar_modalidad(modalidad_id)
        RequisitoModalidadValidator._validar_tipo(tipo)
        RequisitoModalidadValidator._validar_descripcion(descripcion)
        RequisitoModalidadValidator._validar_valor_segun_tipo(tipo, valor_numerico, valor_booleano)
        RequisitoModalidadValidator._validar_unicidad_requisito(modalidad_id, tipo)

    @staticmethod
    def validar_actualizacion(requisito, tipo, descripcion, valor_numerico=None, valor_booleano=None):
        RequisitoModalidadValidator._validar_tipo(tipo)
        RequisitoModalidadValidator._validar_descripcion(descripcion)
        RequisitoModalidadValidator._validar_valor_segun_tipo(tipo, valor_numerico, valor_booleano)
        RequisitoModalidadValidator._validar_unicidad_requisito(
            requisito.modalidad_id, tipo, excluir_id=requisito.pk
        )

    @staticmethod
    def validar_eliminacion(requisito):
        if not requisito.activo:
            raise ValidationError("Este requisito ya se encuentra desactivado.")

    @staticmethod
    def _validar_modalidad(modalidad_id):
        if not modalidad_id:
            raise ValidationError({"modalidad": "La modalidad es obligatoria."})
        if not ModalidadSelector.existe(modalidad_id):
            raise ValidationError({"modalidad": f"No existe una Modalidad con id={modalidad_id}."})

    @staticmethod
    def _validar_tipo(tipo):
        if not tipo:
            raise ValidationError({"tipo": "El tipo de requisito es obligatorio."})
        if tipo not in TIPOS_VALIDOS:
            raise ValidationError(
                {"tipo": f"'{tipo}' no es un tipo de requisito válido. Use uno de: {sorted(TIPOS_VALIDOS)}."}
            )

    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            raise ValidationError({"descripcion": "La descripción del requisito es obligatoria."})

    @staticmethod
    def _validar_valor_segun_tipo(tipo, valor_numerico, valor_booleano):
        if tipo in TIPOS_CON_VALOR_NUMERICO:
            if valor_numerico is None:
                raise ValidationError(
                    {"valor_numerico": f"El requisito de tipo '{tipo}' requiere un valor numérico."}
                )
            try:
                float(valor_numerico)
            except (TypeError, ValueError):
                raise ValidationError({"valor_numerico": "El valor numérico debe ser un número."})
        elif tipo in TIPOS_CON_VALOR_BOOLEANO:
            if valor_booleano is None:
                raise ValidationError(
                    {"valor_booleano": f"El requisito de tipo '{tipo}' requiere un valor booleano (sí/no)."}
                )

    @staticmethod
    def _validar_unicidad_requisito(modalidad_id, tipo, excluir_id=None):
        if RequisitoModalidadSelector.existe_requisito(modalidad_id, tipo, excluir_id=excluir_id):
            raise ValidationError(
                f"Esta modalidad ya tiene un requisito de tipo '{tipo}' registrado."
            )