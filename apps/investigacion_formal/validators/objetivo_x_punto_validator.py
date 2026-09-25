from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.objetivos_selector import ObjetivosSelector
from apps.investigacion_formal.selectors.punto_control_selector import PuntoControlSelector
from apps.investigacion_formal.selectors.objetivo_x_punto_selector import ObjetivoXPuntoSelector

MESES_VALIDOS = {
    'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
    'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE',
}


class ObjetivoXPuntoValidator:

    @staticmethod
    def validar_creacion(objetivo_id, punto_control_id, descripcion_avance, avance,
                          mes_avance, anio_avance):
        ObjetivoXPuntoValidator._validar_objetivo(objetivo_id)
        ObjetivoXPuntoValidator._validar_punto_control(punto_control_id)
        ObjetivoXPuntoValidator._validar_descripcion_avance(descripcion_avance)
        ObjetivoXPuntoValidator._validar_avance(avance)
        ObjetivoXPuntoValidator._validar_mes(mes_avance)
        ObjetivoXPuntoValidator._validar_anio(anio_avance)
        ObjetivoXPuntoValidator._validar_unicidad(objetivo_id, punto_control_id)

    @staticmethod
    def validar_nuevo_avance(descripcion_avance, avance, mes_avance, anio_avance):
        """Reglas para agregarAvanceXPunto: registra un nuevo ObjetivoXPunto
        (histórico) desactivando el anterior — no es una edición in place."""
        ObjetivoXPuntoValidator._validar_descripcion_avance(descripcion_avance)
        ObjetivoXPuntoValidator._validar_avance(avance)
        ObjetivoXPuntoValidator._validar_mes(mes_avance)
        ObjetivoXPuntoValidator._validar_anio(anio_avance)

    @staticmethod
    def validar_eliminacion(objetivo_x_punto):
        if not objetivo_x_punto.estado:
            raise ValidationError("Este avance ya se encuentra desactivado.")

    @staticmethod
    def _validar_objetivo(objetivo_id):
        if not objetivo_id:
            raise ValidationError({"objetivo": "El objetivo es obligatorio."})
        if not ObjetivosSelector.existe(objetivo_id):
            raise ValidationError({"objetivo": f"No existe un Objetivo con id={objetivo_id}."})

    @staticmethod
    def _validar_punto_control(punto_control_id):
        if not punto_control_id:
            raise ValidationError({"punto_control": "El punto de control es obligatorio."})
        if not PuntoControlSelector.existe(punto_control_id):
            raise ValidationError(
                {"punto_control": f"No existe un PuntoControl con id={punto_control_id}."}
            )

    @staticmethod
    def _validar_descripcion_avance(descripcion_avance):
        if not descripcion_avance or not descripcion_avance.strip():
            raise ValidationError(
                {"descripcion_avance": "La descripción del avance es obligatoria."}
            )
        if len(descripcion_avance) > 255:
            raise ValidationError(
                {"descripcion_avance": "La descripción supera el máximo de 255 caracteres."}
            )

    @staticmethod
    def _validar_avance(avance):
        if avance is None:
            raise ValidationError({"avance": "El porcentaje de avance es obligatorio."})
        try:
            valor = float(avance)
        except (TypeError, ValueError):
            raise ValidationError({"avance": "El avance debe ser numérico."})
        if valor < 0 or valor > 100:
            raise ValidationError({"avance": "El avance debe estar entre 0 y 100."})

    @staticmethod
    def _validar_mes(mes_avance):
        if not mes_avance or not mes_avance.strip():
            raise ValidationError({"mes_avance": "El mes del avance es obligatorio."})
        if mes_avance.upper() not in MESES_VALIDOS:
            raise ValidationError(
                {"mes_avance": f"'{mes_avance}' no es un mes válido. Use uno de: {sorted(MESES_VALIDOS)}."}
            )

    @staticmethod
    def _validar_anio(anio_avance):
        if not anio_avance:
            raise ValidationError({"anio_avance": "El año del avance es obligatorio."})

    @staticmethod
    def _validar_unicidad(objetivo_id, punto_control_id, excluir_id=None):
        if ObjetivoXPuntoSelector.existe_vinculo(objetivo_id, punto_control_id, excluir_id=excluir_id):
            raise ValidationError(
                "Ya existe un vínculo registrado entre este objetivo y este punto de control."
            )