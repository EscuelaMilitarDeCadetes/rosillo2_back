from django.db import transaction

from apps.investigacion_formal.models import Convocatoria
from apps.investigacion_formal.selectors.convocatoria_selector import ConvocatoriaSelector
from apps.investigacion_formal.validators.convocatoria_validator import ConvocatoriaValidator
from apps.common.services.historial_service import HistorialService

from rest_framework.exceptions import ValidationError
from apps.common.services.documento_firma_service import DocumentoFirmaService
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector


class ConvocatoriaService:

    @staticmethod
    def listar():
        return ConvocatoriaSelector.listar()

    @staticmethod
    def obtener(convocatoria_id):
        return ConvocatoriaSelector.obtener(convocatoria_id)

    @staticmethod
    def listar_internas(estado=None):
        return ConvocatoriaSelector.listar_internas(estado=estado)
    
    @staticmethod
    def listar_abiertas():
        return ConvocatoriaSelector.listar_abiertas()

    @staticmethod
    @transaction.atomic
    def crear(nombre_convocatoria, anio_convocatoria, inicio, cierre, interno, ejecutor):
        """Creada exclusivamente por el rol ASESOR."""
        ConvocatoriaValidator.validar_creacion(
            nombre_convocatoria, anio_convocatoria, inicio, cierre, interno
        )
        convocatoria = Convocatoria.objects.create(
            nombre_convocatoria=nombre_convocatoria.strip(),
            anio_convocatoria=anio_convocatoria,
            inicio=inicio,
            cierre=cierre,
            interno=interno,
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó la convocatoria '{convocatoria.nombre_convocatoria}' "
            f"({'interna' if interno else 'externa'}, id={convocatoria.pk}).",
            objeto=convocatoria,
        )
        return convocatoria

    @staticmethod
    @transaction.atomic
    def crear_con_documento(nombre_convocatoria, anio_convocatoria, inicio, cierre,
                             interno, archivo, ip_creacion, ejecutor):
        """
        Equivalente al 'newConvocatory' de Thymeleaf: crea la convocatoria y
        registra su documento principal (TipoDocumento 'Convocatoria') en una
        sola operación atómica. Si el registro del documento falla, el
        rollback deshace también la convocatoria.
        """
        if archivo is None:
            raise ValidationError({"archivo": "El documento principal de la convocatoria es obligatorio."})
        convocatoria = ConvocatoriaService.crear(
            nombre_convocatoria=nombre_convocatoria,
            anio_convocatoria=anio_convocatoria,
            inicio=inicio,
            cierre=cierre,
            interno=interno,
            ejecutor=ejecutor,
        )
        tipo_documento = TipoDocumentoSelector.obtener_por_nombre("Convocatoria")
        if tipo_documento is None:
            raise ValidationError(
                "No existe el TipoDocumento 'Convocatoria' (seed pendiente: "
                "grupo='convocatoria', nombre_documento='Convocatoria')."
            )
        DocumentoFirmaService.crear_desde_archivo(
            tipo_documento_id=tipo_documento.pk,
            archivo=archivo,
            ip_creacion=ip_creacion,
            ejecutor=ejecutor,
            objeto=convocatoria,
            estado='FIRMADO',
            carpeta='convocatorias',
        )
        return convocatoria

    @staticmethod
    @transaction.atomic
    def cambiar_estado(convocatoria_id, nuevo_estado, ejecutor):
        """Única modificación permitida sobre una convocatoria; realizada por CINTERNO.
        No se editan ni se borran convocatorias por ningún otro medio."""
        convocatoria = ConvocatoriaSelector.obtener(convocatoria_id)
        ConvocatoriaValidator.validar_cambio_estado(convocatoria, nuevo_estado)

        convocatoria.estado = nuevo_estado
        convocatoria.save(update_fields=['estado'])

        HistorialService.registrar(
            ejecutor,
            f"Se {'activó' if nuevo_estado else 'desactivó'} la convocatoria "
            f"'{convocatoria.nombre_convocatoria}' (id={convocatoria.pk}).",
            objeto=convocatoria,
        )
        return convocatoria