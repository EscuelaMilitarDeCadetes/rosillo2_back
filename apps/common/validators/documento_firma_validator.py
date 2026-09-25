from rest_framework.exceptions import ValidationError
from apps.common.models import DocumentoFirma
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector
from apps.common.selectors.documento_firma_selector import DocumentoFirmaSelector

ESTADOS_VALIDOS = {choice[0] for choice in DocumentoFirma.ESTADO_CHOICES}

# Réplica de ValidarArchivos.pdf() (Thymeleaf). El original tenía
# SIZE_PDF = 1500_000_000 (~1500MB) pese a que el mensaje de la plantilla
# adminConvocatoria.html decía "no superior en tamaño a 15Mb" — era un bug
# del original (le sobraban dos ceros). Aquí se usa el límite realmente
# pretendido: 15MB.
TAMANO_MAXIMO_PDF = 15_000_000  # bytes
TAMANO_MAXIMO_PDF_MB = TAMANO_MAXIMO_PDF // 1_000_000


class DocumentoFirmaValidator:
    @staticmethod
    def validar_creacion(tipo_documento_id, version, ruta_documento, hash_documento, content_type=None, object_id=None, estado='BORRADOR'):
        DocumentoFirmaValidator._validar_tipo_documento(tipo_documento_id)
        DocumentoFirmaValidator._validar_version(version)
        DocumentoFirmaValidator._validar_ruta(ruta_documento)
        DocumentoFirmaValidator._validar_hash(hash_documento)
        DocumentoFirmaValidator._validar_objeto(content_type, object_id)
        DocumentoFirmaValidator._validar_estado(estado)
        DocumentoFirmaValidator._validar_unicidad_version(tipo_documento_id, content_type, object_id, version)
        
    @staticmethod
    def validar_archivo_pdf(archivo):
        """
        Réplica de ValidarArchivos.pdf(): solo se aceptan archivos PDF y de
        máximo TAMANO_MAXIMO_PDF. Se invoca ANTES de escribir el archivo a
        disco (igual que el original validaba antes de Files.write()), desde
        DocumentoFirmaService.crear_desde_archivo() — punto de entrada único
        para todos los módulos (convocatoria, proyecto, presupuesto, etc.),
        así que esta regla aplica de forma centralizada a cualquier documento
        que entre por multipart, sin que cada servicio la reimplemente.
        """
        if archivo is None:
            raise ValidationError({"archivo": "El archivo es obligatorio."})
        content_type = getattr(archivo, "content_type", None)
        if content_type != "application/pdf":
            raise ValidationError(
                {"archivo": "El archivo debe ser de tipo PDF."}
            )
        tamano = getattr(archivo, "size", None)
        if tamano is not None and tamano > TAMANO_MAXIMO_PDF:
            raise ValidationError(
                {"archivo": f"El archivo supera el tamaño máximo permitido de "
                            f"{TAMANO_MAXIMO_PDF_MB}MB."}
            )

    @staticmethod
    def validar_cambio_estado(documento_firma, nuevo_estado):
        DocumentoFirmaValidator._validar_estado(nuevo_estado)
        if documento_firma.estado == 'FIRMADO' and nuevo_estado != 'FIRMADO':
            raise ValidationError(
                "Un documento ya firmado completamente no puede regresar a un estado anterior."
            )

    @staticmethod
    def validar_eliminacion(documento_firma):
        if documento_firma.estado in {'EN_FIRMAS', 'FIRMADO'}:
            raise ValidationError(
                f"No se puede eliminar el documento id={documento_firma.pk}: está en "
                f"estado '{documento_firma.estado}'. Solo se pueden eliminar borradores."
            )

    @staticmethod
    def _validar_tipo_documento(tipo_documento_id):
        if not tipo_documento_id:
            raise ValidationError({"tipo_documento": "El tipo de documento es obligatorio."})
        if not TipoDocumentoSelector.buscar(tipo_documento_id):
            raise ValidationError({"tipo_documento": f"No existe un TipoDocumento con id={tipo_documento_id}."})

    @staticmethod
    def _validar_version(version):
        if not version or version < 1:
            raise ValidationError({"version": "La versión debe ser un entero mayor o igual a 1."})

    @staticmethod
    def _validar_ruta(ruta_documento):
        if not ruta_documento or not ruta_documento.strip():
            raise ValidationError({"ruta_documento": "La ruta del documento es obligatoria."})
        if len(ruta_documento) > 255:
            raise ValidationError({"ruta_documento": "La ruta supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_hash(hash_documento):
        if not hash_documento or not hash_documento.strip():
            raise ValidationError({"hash_documento": "El hash del documento es obligatorio."})
        if len(hash_documento) > 64:
            raise ValidationError({"hash_documento": "El hash supera el máximo de 64 caracteres."})

    @staticmethod
    def _validar_estado(estado):
        if estado not in ESTADOS_VALIDOS:
            raise ValidationError(
                {"estado": f"'{estado}' no es un estado válido. Use uno de: {sorted(ESTADOS_VALIDOS)}."}
            )

    @staticmethod
    def _validar_unicidad_version(tipo_documento_id, content_type, object_id, version, excluir_id=None):
        if DocumentoFirmaSelector.existe_version(tipo_documento_id, content_type, object_id, version, excluir_id=excluir_id):
            raise ValidationError(
                {"version": f"Ya existe la versión {version} para este documento."}
            )
    
    @staticmethod
    def _validar_objeto(content_type, object_id):
        if (content_type is None) != (object_id is None):
            raise ValidationError(
                "content_type y object_id deben enviarse juntos."
            )