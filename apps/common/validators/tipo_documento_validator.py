from apps.common.models.tipo_documento import TipoDocumento
from rest_framework.exceptions import ValidationError
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector


class TipoDocumentoValidator:
    @staticmethod
    def validar_creacion(nombre_documento, grupo, investigacion):
        TipoDocumentoValidator._validar_nombre(nombre_documento)
        TipoDocumentoValidator._validar_grupo(grupo)
        TipoDocumentoValidator._validar_investigacion(investigacion)
        TipoDocumentoValidator._validar_unicidad_nombre(nombre_documento)

    @staticmethod
    def validar_actualizacion(tipo_documento_id, nombre_documento, grupo, investigacion):
        TipoDocumentoValidator._validar_nombre(nombre_documento)
        TipoDocumentoValidator._validar_grupo(grupo)
        TipoDocumentoValidator._validar_investigacion(investigacion)
        TipoDocumentoValidator._validar_unicidad_nombre(nombre_documento, excluir_id=tipo_documento_id)

    @staticmethod
    def _validar_nombre(nombre_documento):
        if not nombre_documento or not nombre_documento.strip():
            raise ValidationError({"nombre_documento": "El nombre del documento es obligatorio."})
        if len(nombre_documento) > 40:
            raise ValidationError(
                {"nombre_documento": f"El nombre '{nombre_documento}' supera el máximo de 40 caracteres."}
            )

    @staticmethod
    def _validar_grupo(grupo):
        if not grupo or not grupo.strip():
            raise ValidationError({"grupo": "El grupo del tipo de documento es obligatorio."})
        if len(grupo) > 30:
            raise ValidationError({"grupo": "El grupo supera el máximo de 30 caracteres."})

    @staticmethod
    def _validar_unicidad_nombre(nombre_documento, excluir_id=None):
        if TipoDocumentoSelector.existe_nombre(nombre_documento, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_documento": f"Ya existe un tipo de documento con el nombre '{nombre_documento}'."}
            )
            
    @staticmethod
    def _validar_investigacion(investigacion):
        validos = {c[0] for c in TipoDocumento.INVESTIGACION_CHOICES}
        if investigacion is not None and investigacion not in validos:
            raise ValidationError({"investigacion": f"Debe ser uno de: {sorted(validos)}."})