from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.segunda_instancia_selector import (
    SegundaInstanciaSelector,
)
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)
from apps.investigacion_formativa.selectors.instancia_etapa_selector import InstanciaEtapaSelector
from apps.investigacion_formativa.selectors.evaluacion_proceso_selector import (
    EvaluacionProcesoSelector,
)
from apps.investigacion_formativa.selectors.etapa_flujo_selector import EtapaFlujoSelector

TIPOS_VALIDOS = {'TUTOR', 'JURADO', 'SUSTENTACION', 'ANTIPLAGIO'}


class SegundaInstanciaValidator:

    @staticmethod
    def validar_creacion(proceso_id, instancia_etapa_id, evaluacion_id, etapa_retorno_id,
                          tipo, motivo, nota_maxima=3.5):
        SegundaInstanciaValidator._validar_proceso(proceso_id)
        SegundaInstanciaValidator._validar_instancia_etapa(instancia_etapa_id)
        SegundaInstanciaValidator._validar_evaluacion(evaluacion_id)
        SegundaInstanciaValidator._validar_etapa_retorno(etapa_retorno_id)
        SegundaInstanciaValidator._validar_tipo(tipo)
        SegundaInstanciaValidator._validar_motivo(motivo)
        SegundaInstanciaValidator._validar_nota_maxima(nota_maxima)

    @staticmethod
    def validar_activacion(segunda_instancia):
        if not segunda_instancia.activa:
            raise ValidationError("No se puede activar una segunda instancia que ya está desactivada.")
        if segunda_instancia.activada:
            raise ValidationError("Esta segunda instancia ya se encuentra activada.")

    @staticmethod
    def validar_consumo(segunda_instancia):
        """Se marca 'consumida' cuando el proceso agota su oportunidad de segunda instancia."""
        if not segunda_instancia.activada:
            raise ValidationError("Esta segunda instancia debe activarse antes de poder consumirse.")
        if segunda_instancia.consumida:
            raise ValidationError("Esta segunda instancia ya fue consumida.")

    @staticmethod
    def validar_eliminacion(segunda_instancia):
        if not segunda_instancia.activa:
            raise ValidationError("Esta segunda instancia ya se encuentra desactivada.")

    @staticmethod
    def _validar_proceso(proceso_id):
        if not proceso_id:
            raise ValidationError({"proceso": "El proceso formativo es obligatorio."})
        if not ProcesoFormativoSelector.existe(proceso_id):
            raise ValidationError({"proceso": f"No existe un ProcesoFormativo con id={proceso_id}."})
        if SegundaInstanciaSelector.existe_para_proceso(proceso_id):
            raise ValidationError("Este proceso formativo ya tiene una segunda instancia registrada.")

    @staticmethod
    def _validar_instancia_etapa(instancia_etapa_id):
        if not instancia_etapa_id:
            raise ValidationError({"instancia_etapa": "La instancia de etapa es obligatoria."})
        if not InstanciaEtapaSelector.existe(instancia_etapa_id):
            raise ValidationError(
                {"instancia_etapa": f"No existe una InstanciaEtapa con id={instancia_etapa_id}."}
            )

    @staticmethod
    def _validar_evaluacion(evaluacion_id):
        if not evaluacion_id:
            raise ValidationError({"evaluacion": "La evaluación que originó la segunda instancia es obligatoria."})
        if not EvaluacionProcesoSelector.existe(evaluacion_id):
            raise ValidationError({"evaluacion": f"No existe una EvaluacionProceso con id={evaluacion_id}."})

    @staticmethod
    def _validar_etapa_retorno(etapa_retorno_id):
        if not etapa_retorno_id:
            raise ValidationError({"etapa_retorno": "La etapa de retorno es obligatoria."})
        if not EtapaFlujoSelector.existe(etapa_retorno_id):
            raise ValidationError({"etapa_retorno": f"No existe una EtapaFlujo con id={etapa_retorno_id}."})

    @staticmethod
    def _validar_tipo(tipo):
        if not tipo:
            raise ValidationError({"tipo": "El tipo de segunda instancia es obligatorio."})
        if tipo not in TIPOS_VALIDOS:
            raise ValidationError(
                {"tipo": f"'{tipo}' no es un tipo válido. Use uno de: {sorted(TIPOS_VALIDOS)}."}
            )

    @staticmethod
    def _validar_motivo(motivo):
        if not motivo or not motivo.strip():
            raise ValidationError({"motivo": "El motivo de la segunda instancia es obligatorio."})

    @staticmethod
    def _validar_nota_maxima(nota_maxima):
        if nota_maxima is None:
            raise ValidationError({"nota_maxima": "La nota máxima alcanzable en segunda instancia es obligatoria."})
        try:
            valor = float(nota_maxima)
        except (TypeError, ValueError):
            raise ValidationError({"nota_maxima": "La nota máxima debe ser numérica."})
        if valor < 0 or valor > 5:
            raise ValidationError({"nota_maxima": "La nota máxima debe estar entre 0.0 y 5.0."})