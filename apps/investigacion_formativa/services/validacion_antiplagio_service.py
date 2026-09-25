from django.db import transaction

from apps.investigacion_formativa.models import ValidacionAntiplagio
from apps.investigacion_formativa.selectors.validacion_antiplagio_selector import (
    ValidacionAntiplagioSelector,
)
from apps.investigacion_formativa.validators.validacion_antiplagio_validator import (
    ValidacionAntiplagioValidator,
)
from apps.common.services.historial_service import HistorialService


class ValidacionAntiplagioService:

    @staticmethod
    def listar():
        return ValidacionAntiplagioSelector.listar()

    @staticmethod
    def obtener(validacion_id):
        return ValidacionAntiplagioSelector.obtener(validacion_id)

    @staticmethod
    def listar_por_instancia_etapa(instancia_etapa_id):
        return ValidacionAntiplagioSelector.listar_por_instancia_etapa(instancia_etapa_id)

    @staticmethod
    @transaction.atomic
    def crear(instancia_etapa_id, documento_id, porcentaje, aprobado, ejecutor):
        ValidacionAntiplagioValidator.validar_creacion(
            instancia_etapa_id, documento_id, porcentaje, aprobado
        )
        validacion = ValidacionAntiplagio.objects.create(
            instancia_etapa_id=instancia_etapa_id,
            documento_id=documento_id,
            porcentaje=porcentaje,
            aprobado=aprobado,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró la validación de antiplagio del documento (id documento="
            f"{documento_id}) con {porcentaje}% de similitud (id={validacion.pk}).",
            objeto=validacion,
        )
        return validacion

    @staticmethod
    @transaction.atomic
    def actualizar(validacion_id, porcentaje, aprobado, ejecutor):
        validacion = ValidacionAntiplagioSelector.obtener(validacion_id)
        ValidacionAntiplagioValidator.validar_actualizacion(validacion, porcentaje, aprobado)
        validacion.porcentaje = porcentaje
        validacion.aprobado = aprobado
        validacion.save(update_fields=['porcentaje', 'aprobado'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la validación de antiplagio (id={validacion.pk}) a "
            f"{porcentaje}% de similitud.",
            objeto=validacion,
        )
        return validacion