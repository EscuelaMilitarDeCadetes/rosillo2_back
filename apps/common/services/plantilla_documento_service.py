from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.common.models import TipoDocumento
from apps.common.models import PlantillaDocumento
from apps.common.selectors.plantilla_documento_selector import PlantillaDocumentoSelector
from apps.common.validators.plantilla_documento_validator import PlantillaDocumentoValidator
from apps.common.services.historial_service import HistorialService


class PlantillaDocumentoService:
    @staticmethod
    def listar(investigacion=None):
        return PlantillaDocumentoSelector.listar(investigacion=investigacion)

    @staticmethod
    def validar_ambito_tipo_documento(tipo_documento_id, investigacion):
        """Sólo se pueden gestionar plantillas de tipos de documento del
        módulo (formal/formativa) con el que se inició sesión."""
        if investigacion is None:
            return
        tipo = TipoDocumento.objects.filter(pk=tipo_documento_id).first()
        if tipo is not None and tipo.investigacion != investigacion:
            raise ValidationError({
                "tipo_documento": (
                    f"El tipo de documento '{tipo.nombre_documento}' no pertenece a "
                    f"Investigación {investigacion.capitalize()}, el módulo con el que iniciaste sesión."
                )
            })

    @staticmethod
    def obtener(plantilla_id):
        return PlantillaDocumentoSelector.obtener(plantilla_id)

    @staticmethod
    @transaction.atomic
    def crear(tipo_documento_id, ruta_documento, ejecutor, investigacion=None):
        PlantillaDocumentoValidator.validar_creacion(tipo_documento_id, ruta_documento)
        PlantillaDocumentoService.validar_ambito_tipo_documento(tipo_documento_id, investigacion)
        plantilla = PlantillaDocumento.objects.create(
            tipo_documento_id=tipo_documento_id,
            ruta_documento=ruta_documento.strip(),
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró la plantilla para el tipo de documento "
            f"'{plantilla.tipo_documento.nombre_documento}' (id={plantilla.pk}).",
            objeto=plantilla,
        )
        return plantilla

    @staticmethod
    @transaction.atomic
    def actualizar(plantilla_id, ejecutor, ruta_documento, investigacion=None):
        plantilla = PlantillaDocumentoSelector.obtener(plantilla_id)
        PlantillaDocumentoService.validar_ambito_tipo_documento(plantilla.tipo_documento_id, investigacion)
        PlantillaDocumentoValidator.validar_actualizacion(
            plantilla_id, plantilla.tipo_documento_id, ruta_documento
        )
        plantilla.ruta_documento = ruta_documento.strip()
        plantilla.save(update_fields=['ruta_documento'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la ruta de la plantilla del tipo de documento "
            f"'{plantilla.tipo_documento.nombre_documento}' (id={plantilla.pk}).",
            objeto=plantilla,
        )
        return plantilla

    @staticmethod
    @transaction.atomic
    def desactivar(plantilla_id, ejecutor, investigacion=None):
        plantilla = PlantillaDocumentoSelector.obtener(plantilla_id)
        PlantillaDocumentoService.validar_ambito_tipo_documento(plantilla.tipo_documento_id, investigacion)
        plantilla.estado = False
        plantilla.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó la plantilla del tipo de documento "
            f"'{plantilla.tipo_documento.nombre_documento}' (id={plantilla.pk}).",
            objeto=plantilla,
        )
        return plantilla

    @staticmethod
    def obtener_por_tipo_documento(tipo_documento_id):
        return PlantillaDocumentoSelector.obtener_por_tipo_documento(tipo_documento_id)