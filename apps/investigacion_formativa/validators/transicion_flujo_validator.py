# apps/investigacion_formativa/validators/transicion_flujo_validator.py
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.transicion_flujo_selector import (
    TransicionFlujoSelector,
)
from apps.investigacion_formativa.selectors.etapa_flujo_selector import EtapaFlujoSelector

NOMBRE_MAX_LEN = 100
ACCION_AUTOMATICA_MAX_LEN = 100


class TransicionFlujoValidator:

    @staticmethod
    def validar_creacion(etapa_origen_id, etapa_destino_id, nombre, condicion=None,
                          accion_automatica=None, orden=0):
        TransicionFlujoValidator._validar_etapa_origen(etapa_origen_id)
        TransicionFlujoValidator._validar_etapa_destino(etapa_destino_id)
        TransicionFlujoValidator._validar_nombre(nombre)
        TransicionFlujoValidator._validar_accion_automatica(accion_automatica)
        TransicionFlujoValidator._validar_orden(orden)
        TransicionFlujoValidator._validar_unicidad(etapa_origen_id, etapa_destino_id)

    @staticmethod
    def validar_actualizacion(transicion, etapa_origen_id, etapa_destino_id, nombre,
                               condicion=None, accion_automatica=None, orden=0):
        TransicionFlujoValidator._validar_etapa_origen(etapa_origen_id)
        TransicionFlujoValidator._validar_etapa_destino(etapa_destino_id)
        TransicionFlujoValidator._validar_nombre(nombre)
        TransicionFlujoValidator._validar_accion_automatica(accion_automatica)
        TransicionFlujoValidator._validar_orden(orden)
        TransicionFlujoValidator._validar_unicidad(
            etapa_origen_id, etapa_destino_id, excluir_id=transicion.pk
        )

    @staticmethod
    def validar_activacion(transicion):
        if transicion.activo:
            raise ValidationError("Esta transición ya se encuentra activa.")

    @staticmethod
    def validar_desactivacion(transicion):
        if not transicion.activo:
            raise ValidationError("Esta transición ya se encuentra desactivada.")

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
            raise ValidationError({"nombre": "El nombre descriptivo de la transición es obligatorio."})
        if len(nombre) > NOMBRE_MAX_LEN:
            raise ValidationError({"nombre": f"El nombre supera el máximo de {NOMBRE_MAX_LEN} caracteres."})

    @staticmethod
    def _validar_accion_automatica(accion_automatica):
        if accion_automatica and len(accion_automatica) > ACCION_AUTOMATICA_MAX_LEN:
            raise ValidationError(
                {"accion_automatica": f"La acción automática supera el máximo de {ACCION_AUTOMATICA_MAX_LEN} caracteres."}
            )

    @staticmethod
    def _validar_orden(orden):
        if orden is None:
            raise ValidationError({"orden": "El orden de evaluación de la transición es obligatorio."})
        if not isinstance(orden, int) or orden < 0:
            raise ValidationError({"orden": "El orden debe ser un entero no negativo."})

    @staticmethod
    def _validar_unicidad(etapa_origen_id, etapa_destino_id, excluir_id=None):
        if TransicionFlujoSelector.existe_transicion(etapa_origen_id, etapa_destino_id, excluir_id=excluir_id):
            raise ValidationError(
                "Ya existe una transición registrada entre estas mismas etapas de origen y destino."
            )