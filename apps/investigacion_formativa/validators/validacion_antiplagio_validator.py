from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.validacion_antiplagio_selector import (
    ValidacionAntiplagioSelector,
)
from apps.investigacion_formativa.selectors.instancia_etapa_selector import InstanciaEtapaSelector


class ValidacionAntiplagioValidator:

    @staticmethod
    def validar_creacion(instancia_etapa_id, documento_id, porcentaje, aprobado):
        ValidacionAntiplagioValidator._validar_instancia_etapa(instancia_etapa_id)
        ValidacionAntiplagioValidator._validar_documento(documento_id)
        ValidacionAntiplagioValidator._validar_porcentaje(porcentaje)
        ValidacionAntiplagioValidator._validar_aprobado(aprobado)
        ValidacionAntiplagioValidator._validar_unicidad(instancia_etapa_id, documento_id)

    @staticmethod
    def validar_actualizacion(validacion, porcentaje, aprobado):
        """instancia_etapa y documento forman la llave compuesta y no se reasignan."""
        ValidacionAntiplagioValidator._validar_porcentaje(porcentaje)
        ValidacionAntiplagioValidator._validar_aprobado(aprobado)

    @staticmethod
    def _validar_instancia_etapa(instancia_etapa_id):
        if not instancia_etapa_id:
            raise ValidationError({"instancia_etapa": "La instancia de etapa es obligatoria."})
        if not InstanciaEtapaSelector.existe(instancia_etapa_id):
            raise ValidationError(
                {"instancia_etapa": f"No existe una InstanciaEtapa con id={instancia_etapa_id}."}
            )

    @staticmethod
    def _validar_documento(documento_id):
        if not documento_id:
            raise ValidationError({"documento": "El documento a validar es obligatorio."})
        # Import diferido: common no es dependencia directa de investigacion_formativa
        from apps.common.models import DocumentoFirma

        if not DocumentoFirma.objects.filter(pk=documento_id).exists():
            raise ValidationError({"documento": f"No existe un DocumentoFirma con id={documento_id}."})

    @staticmethod
    def _validar_porcentaje(porcentaje):
        if porcentaje is None:
            raise ValidationError({"porcentaje": "El porcentaje de similitud es obligatorio."})
        try:
            valor = float(porcentaje)
        except (TypeError, ValueError):
            raise ValidationError({"porcentaje": "El porcentaje debe ser numérico."})
        if valor < 0 or valor > 100:
            raise ValidationError({"porcentaje": "El porcentaje debe estar entre 0 y 100."})

    @staticmethod
    def _validar_aprobado(aprobado):
        if aprobado is None:
            raise ValidationError({"aprobado": "Debe indicar si el documento aprobó la validación de antiplagio."})

    @staticmethod
    def _validar_unicidad(instancia_etapa_id, documento_id):
        if ValidacionAntiplagioSelector.existe_validacion(instancia_etapa_id, documento_id):
            raise ValidationError(
                "Ya existe una validación de antiplagio registrada para este documento en esta instancia de etapa."
            )