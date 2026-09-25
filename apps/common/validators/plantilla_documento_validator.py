from rest_framework.exceptions import ValidationError
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector
from apps.common.selectors.plantilla_documento_selector import PlantillaDocumentoSelector


class PlantillaDocumentoValidator:
    @staticmethod
    def validar_creacion(tipo_documento_id, ruta_documento):
        PlantillaDocumentoValidator._validar_tipo_documento(tipo_documento_id)
        PlantillaDocumentoValidator._validar_ruta(ruta_documento)
        PlantillaDocumentoValidator._validar_unicidad(tipo_documento_id)

    @staticmethod
    def validar_actualizacion(plantilla_id, tipo_documento_id, ruta_documento):
        PlantillaDocumentoValidator._validar_tipo_documento(tipo_documento_id)
        PlantillaDocumentoValidator._validar_ruta(ruta_documento)
        PlantillaDocumentoValidator._validar_unicidad(tipo_documento_id, excluir_id=plantilla_id)

    @staticmethod
    def _validar_tipo_documento(tipo_documento_id):
        if not tipo_documento_id:
            raise ValidationError({"tipo_documento": "El tipo de documento es obligatorio."})
        if not TipoDocumentoSelector.buscar(tipo_documento_id):
            raise ValidationError({"tipo_documento": f"No existe un TipoDocumento con id={tipo_documento_id}."})

    @staticmethod
    def _validar_ruta(ruta_documento):
        if not ruta_documento or not ruta_documento.strip():
            raise ValidationError({"ruta_documento": "La ruta de la plantilla es obligatoria."})
        if len(ruta_documento) > 255:
            raise ValidationError({"ruta_documento": "La ruta supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_unicidad(tipo_documento_id, excluir_id=None):
        if PlantillaDocumentoSelector.existe_para_tipo_documento(tipo_documento_id, excluir_id=excluir_id):
            raise ValidationError("Ya existe una plantilla registrada para este tipo de documento.")