import hashlib
from django.db import transaction
from apps.common.models import DocumentoFirma
from apps.common.selectors.documento_firma_selector import DocumentoFirmaSelector
from apps.common.validators.documento_firma_validator import DocumentoFirmaValidator
from apps.common.services.historial_service import HistorialService
from rest_framework.exceptions import ValidationError

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.common.services.notificacion_service import NotificacionService

Usuario = get_user_model()
logger = logging.getLogger(__name__)


class DocumentoFirmaService:
    @staticmethod
    def listar():
        return DocumentoFirmaSelector.listar()

    @staticmethod
    def obtener(documento_firma_id):
        return DocumentoFirmaSelector.obtener(documento_firma_id)

    @staticmethod
    @transaction.atomic
    def crear(tipo_documento_id, ruta_documento, ip_creacion, ejecutor, objeto=None, estado='BORRADOR'):
        """
        `objeto` (opcional) es la instancia de negocio a la que pertenece este
        documento (Proyecto, Convocatoria, Presupuesto, ProcesoFormativo...).
        `estado`: 'BORRADOR' (default) para documentos nuevos que van a pasar
        por el flujo de firmas dentro de la plataforma. 'FIRMADO' para
        documentos del repositorio histórico (2020+) que ya vienen firmados
        (con todas o algunas firmas) fuera de la plataforma y no se espera
        que nadie los firme aquí.
        """
        ultima = DocumentoFirmaSelector.obtener_ultima_version(tipo_documento_id, objeto)
        version = (ultima.version + 1) if ultima else 1
        try:
            with open(ruta_documento, "rb") as archivo:
                hash_documento = hashlib.sha256(archivo.read()).hexdigest()
        except FileNotFoundError:
            raise ValidationError({
                "ruta_documento": (
                    f"No se encontró el archivo en la ruta '{ruta_documento}'. "
                    "El documento debe existir físicamente en disco antes de registrar su firma."
                )
            })
        datos = dict(
            tipo_documento_id=tipo_documento_id,
            version=version,
            ruta_documento=ruta_documento,
            estado=estado,
            hash_documento=hash_documento,
            ip_creacion=ip_creacion,
            habilitado_firma=False,
        )
        if objeto is not None:
            from django.contrib.contenttypes.models import ContentType
            datos["content_type"] = ContentType.objects.get_for_model(objeto)
            datos["object_id"] = objeto.pk

        DocumentoFirmaValidator.validar_creacion(
            tipo_documento_id, version, ruta_documento, hash_documento,
            datos.get("content_type"), datos.get("object_id"), estado=estado,
        )
        documento = DocumentoFirma.objects.create(**datos)
        HistorialService.registrar(
            ejecutor,
            f"Se creó el documento '{documento.tipo_documento.nombre_documento}' "
            f"versión {documento.version} en estado {estado} (id={documento.pk}).",
            objeto=documento,
        )
        return documento

    @staticmethod
    @transaction.atomic
    def crear_desde_archivo(tipo_documento_id, archivo, ip_creacion, ejecutor,
                             objeto=None, estado='BORRADOR', carpeta='documentos'):
        """
        Punto de entrada único para crear un DocumentoFirma a partir de un
        archivo subido por multipart (UploadedFile de Django), en vez de una
        ruta ya existente en disco. Centraliza la escritura física del
        archivo para que ConvocatoriaService, y en el futuro ProyectoService,
        PresupuestoService, ProcesoFormativoService, etc., no reimplementen
        default_storage.save() cada uno por su cuenta.
        `carpeta`: subcarpeta dentro de MEDIA_ROOT para organizar por
        dominio ('convocatorias', 'proyectos', 'presupuestos', ...).
        """
        DocumentoFirmaValidator.validar_archivo_pdf(archivo)
        ruta_relativa = default_storage.save(f"{carpeta}/{archivo.name}", ContentFile(archivo.read()))
        ruta_documento = default_storage.path(ruta_relativa)
        from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector
        tipo_documento = TipoDocumentoSelector.buscar(tipo_documento_id)
        if tipo_documento and tipo_documento.es_informe_seguimiento:
            DocumentoFirmaService._marcar_si_es_tardio(ruta_documento)
        return DocumentoFirmaService.crear(
            tipo_documento_id=tipo_documento_id,
            ruta_documento=ruta_documento,
            ip_creacion=ip_creacion,
            ejecutor=ejecutor,
            objeto=objeto,
            estado=estado,
        )

    @staticmethod
    @transaction.atomic
    def habilitar_para_firma(documento_firma_id, ejecutor):
        documento = DocumentoFirmaSelector.obtener(documento_firma_id)
        DocumentoFirmaValidator.validar_cambio_estado(documento, 'EN_FIRMAS')
        documento.estado = 'EN_FIRMAS'
        documento.habilitado_firma = True
        documento.save(update_fields=['estado', 'habilitado_firma'])
        HistorialService.registrar(
            ejecutor,
            f"Se habilitó para firma el documento '{documento.tipo_documento.nombre_documento}' "
            f"versión {documento.version} (id={documento.pk}).",
            objeto=documento,
        )
        return documento

    @staticmethod
    @transaction.atomic
    def marcar_rechazado(documento_firma_id, ejecutor):
        documento = DocumentoFirmaSelector.obtener(documento_firma_id)
        DocumentoFirmaValidator.validar_cambio_estado(documento, 'RECHAZADO')
        documento.estado = 'RECHAZADO'
        documento.habilitado_firma = False
        documento.save(update_fields=['estado', 'habilitado_firma'])
        HistorialService.registrar(
            ejecutor,
            f"El documento '{documento.tipo_documento.nombre_documento}' versión "
            f"{documento.version} quedó en estado RECHAZADO (id={documento.pk}).",
            objeto=documento,
        )
        return documento

    @staticmethod
    @transaction.atomic
    def marcar_firmado_completamente(documento_firma_id, ejecutor):
        documento = DocumentoFirmaSelector.obtener(documento_firma_id)
        DocumentoFirmaValidator.validar_cambio_estado(documento, 'FIRMADO')
        documento.estado = 'FIRMADO'
        documento.habilitado_firma = False
        documento.save(update_fields=['estado', 'habilitado_firma'])
        HistorialService.registrar(
            ejecutor,
            f"El documento '{documento.tipo_documento.nombre_documento}' versión "
            f"{documento.version} quedó completamente FIRMADO (id={documento.pk}).",
            objeto=documento,
        )
        return documento

    @staticmethod
    @transaction.atomic
    def eliminar(documento_firma_id, ejecutor):
        documento = DocumentoFirmaSelector.obtener(documento_firma_id)
        DocumentoFirmaValidator.validar_eliminacion(documento)
        descripcion = (
            f"Se eliminó el documento '{documento.tipo_documento.nombre_documento}' "
            f"versión {documento.version} en estado BORRADOR (id={documento.pk})."
        )
        HistorialService.registrar(ejecutor, descripcion)
        documento.delete()
        return True

    @staticmethod
    def listar_por_tipo_documento(tipo_documento_id):
        return DocumentoFirmaSelector.listar_por_tipo_documento(tipo_documento_id)

    @staticmethod
    def obtener_ultima_version(tipo_documento_id, objeto=None):
        return DocumentoFirmaSelector.obtener_ultima_version(tipo_documento_id, objeto)

    @staticmethod
    def listar_habilitados_para_firma():
        return DocumentoFirmaSelector.listar_habilitados_para_firma()

    @staticmethod
    def listar_por_objeto(objeto):
        """Depende del campo content_type/object_id propuesto. 🔶"""
        return DocumentoFirmaSelector.listar_por_objeto(objeto)

    @staticmethod
    @transaction.atomic
    def verificar_integridad(documento_firma_id):
        """
        Recalcula el hash del archivo en disco y lo compara contra
        hash_documento (calculado una única vez en crear()). No modifica
        estado ni ruta_documento — solo dos campos de monitoreo — y nunca
        lanza excepción hacia el llamador: la task que la invoke necesita
        seguir con el resto de documentos aunque uno falle.
        """
        documento = DocumentoFirmaSelector.obtener(documento_firma_id)
        try:
            with open(documento.ruta_documento, "rb") as archivo:
                hash_actual = hashlib.sha256(archivo.read()).hexdigest()
        except FileNotFoundError:
            documento.integridad_ok = False
            documento.fecha_ultima_verificacion_integridad = timezone.now()
            documento.save(update_fields=['integridad_ok', 'fecha_ultima_verificacion_integridad'])
            DocumentoFirmaService._alertar_integridad(
                documento,
                f"El archivo ya no existe en la ruta '{documento.ruta_documento}'."
            )
            return False
        coincide = (hash_actual == documento.hash_documento)
        documento.integridad_ok = coincide
        documento.fecha_ultima_verificacion_integridad = timezone.now()
        documento.save(update_fields=['integridad_ok', 'fecha_ultima_verificacion_integridad'])
        if not coincide:
            DocumentoFirmaService._alertar_integridad(
                documento,
                f"El hash del archivo en disco no coincide con el registrado "
                f"(esperado {documento.hash_documento[:12]}…, actual {hash_actual[:12]}…)."
            )
        return coincide

    @staticmethod
    def _alertar_integridad(documento, detalle):
        HistorialService.registrar(
            None,  # ejecutor=None -> Historial lo muestra como "SISTEMA"
            f"ALERTA DE INTEGRIDAD: '{documento.tipo_documento.nombre_documento}' "
            f"versión {documento.version} (id={documento.pk}). {detalle}",
            objeto=documento,
        )
        for superusuario in Usuario.objects.filter(is_superuser=True, is_active=True):
            NotificacionService.crear(
                usuario_destino_id=superusuario.pk,
                mensaje=(
                    f"Posible alteración fuera de la plataforma en el documento "
                    f"'{documento.tipo_documento.nombre_documento}' v{documento.version}. {detalle}"
                ),
                tipo='error',
                notificar_email=True,
            )

    @staticmethod
    def verificar_integridad_todos():
        """Recorre todos los documentos; aísla fallos por documento para que
        uno corrupto/ilegible no detenga la corrida completa."""
        resultados = {'verificados': 0, 'alterados': 0}
        for documento in DocumentoFirmaSelector.listar_para_verificar_integridad():
            try:
                ok = DocumentoFirmaService.verificar_integridad(documento.pk)
                resultados['verificados'] += 1
                if not ok:
                    resultados['alterados'] += 1
            except Exception:
                logger.exception(f"Fallo verificando integridad del documento id={documento.pk}")
        return resultados
    
    @staticmethod
    def _marcar_si_es_tardio(ruta_documento):
        """
        Si hoy ya pasó el día límite del mes (settings.DIA_LIMITE_INFORME_SEGUIMIENTO),
        estampa la nota de entrega tardía ANTES de que crear() calcule el hash —
        así el hash de integridad queda calculado sobre el archivo ya anotado,
        y verificar_integridad() nunca reporta un falso "archivo alterado".
        """
        from django.conf import settings
        hoy = timezone.now()
        if hoy.day <= settings.DIA_LIMITE_INFORME_SEGUIMIENTO:
            return
        texto_nota = (
            f"Se entrega después de la fecha estipulada, "
            f"fecha de recepción del documento {hoy.strftime('%d/%m/%Y')}."
        )
        DocumentoFirmaService._estampar_nota_pie(ruta_documento, texto_nota)

    @staticmethod
    def _estampar_nota_pie(ruta_documento, texto_nota):
        """Overlay con reportlab fusionado (pypdf) en el pie de la última página."""
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from pypdf import PdfReader, PdfWriter
        try:
            reader = PdfReader(ruta_documento)
        except Exception:
            logger.exception(
                f"No se pudo leer el PDF en '{ruta_documento}' para estampar la nota de entrega tardía."
            )
            return
        if not reader.pages:
            return
        ultima_pagina = reader.pages[-1]
        ancho = float(ultima_pagina.mediabox.width)
        alto = float(ultima_pagina.mediabox.height)
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(ancho, alto))
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(30, 20, texto_nota)
        c.save()
        buffer.seek(0)
        ultima_pagina.merge_page(PdfReader(buffer).pages[0])
        writer = PdfWriter()
        for pagina in reader.pages:
            writer.add_page(pagina)
        with open(ruta_documento, "wb") as f:
            writer.write(f)

    @staticmethod
    def notificar_cinterno_carga(documento, ejecutor):
        """
        Notifica al único usuario CINTERNO activo (regla de negocio: solo puede
        haber uno activo a la vez) cuando FACULTAD/GRUPO cargan un documento de
        gestión del proyecto, para que sepa cómo se modificó.
        """
        from apps.usuarios.models import RolXUsuario
        cinterno = (
            RolXUsuario.objects
            .filter(rol__nombre_rol='CINTERNO', estado=True, usuario__is_active=True)
            .select_related('usuario')
            .first()
        )
        if cinterno is None:
            return
        objeto_desc = str(documento.objeto_relacionado) if documento.objeto_relacionado else "un proyecto"
        NotificacionService.crear(
            usuario_destino_id=cinterno.usuario_id,
            mensaje=(
                f"'{ejecutor.username}' cargó el documento "
                f"'{documento.tipo_documento.nombre_documento}' (versión {documento.version}) "
                f"en {objeto_desc}."
            ),
            tipo='info',
            notificar_email=True,
        )