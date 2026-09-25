# apps/investigacion_formativa/validators/instancia_etapa_validator.py
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.instancia_etapa_selector import InstanciaEtapaSelector

ESTADOS_VALIDOS = ('PENDIENTE', 'EN_PROCESO', 'APROBADO', 'RECHAZADO', 'SEGUNDA_INSTANCIA')

TRANSICIONES_PERMITIDAS = {
    'PENDIENTE': ('EN_PROCESO',),
    'EN_PROCESO': ('APROBADO', 'RECHAZADO'),
    'RECHAZADO': ('SEGUNDA_INSTANCIA', 'EN_PROCESO'),
    'SEGUNDA_INSTANCIA': ('APROBADO', 'RECHAZADO'),
    'APROBADO': (),
}


class InstanciaEtapaValidator:

    @staticmethod
    def validar_creacion(proceso_id, etapa_id):
        InstanciaEtapaValidator._validar_unicidad(proceso_id, etapa_id)

    @staticmethod
    def validar_inicio(instancia):
        """PENDIENTE -> EN_PROCESO, se ejecuta al habilitar la etapa vigente del proceso."""
        InstanciaEtapaValidator._validar_transicion(instancia.estado, 'EN_PROCESO')

    @staticmethod
    def validar_aprobacion(instancia):
        InstanciaEtapaValidator._validar_transicion(instancia.estado, 'APROBADO')

    @staticmethod
    def validar_rechazo(instancia):
        InstanciaEtapaValidator._validar_transicion(instancia.estado, 'RECHAZADO')

    @staticmethod
    def validar_paso_a_segunda_instancia(instancia):
        InstanciaEtapaValidator._validar_transicion(instancia.estado, 'SEGUNDA_INSTANCIA')

    @staticmethod
    def _validar_transicion(estado_actual, nuevo_estado):
        permitidos = TRANSICIONES_PERMITIDAS.get(estado_actual, ())
        if nuevo_estado not in permitidos:
            raise ValidationError(
                f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}'. "
                f"Transiciones permitidas desde '{estado_actual}': {', '.join(permitidos) or 'ninguna'}."
            )

    @staticmethod
    def _validar_unicidad(proceso_id, etapa_id, excluir_id=None):
        if InstanciaEtapaSelector.existe_etapa_en_proceso(proceso_id, etapa_id, excluir_id=excluir_id):
            raise ValidationError("Ya existe una instancia de esta etapa para este proceso.")