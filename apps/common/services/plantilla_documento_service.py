from django.db import transaction
from apps.common.models import PlantillaDocumento
from apps.common.selectors.plantilla_documento_selector import PlantillaDocumentoSelector
from apps.common.validators.plantilla_documento_validator import PlantillaDocumentoValidator
from apps.common.services.historial_service import HistorialService


class PlantillaDocumentoService:
    @staticmethod
    def listar():
        return PlantillaDocumentoSelector.listar()

    @staticmethod
    def obtener(plantilla_id):
        return PlantillaDocumentoSelector.obtener(plantilla_id)

    @staticmethod
    @transaction.atomic
    def crear(tipo_documento_id, ruta_documento, ejecutor):
        PlantillaDocumentoValidator.validar_creacion(tipo_documento_id, ruta_documento)
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
    def actualizar(plantilla_id, ejecutor, ruta_documento):
        plantilla = PlantillaDocumentoSelector.obtener(plantilla_id)
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
    def desactivar(plantilla_id, ejecutor):
        plantilla = PlantillaDocumentoSelector.obtener(plantilla_id)
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