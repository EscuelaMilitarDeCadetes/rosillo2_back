from django.db import transaction
from apps.common.models import TipoDocumento
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector
from apps.common.services.historial_service import HistorialService
from apps.common.validators.tipo_documento_validator import TipoDocumentoValidator


class TipoDocumentoService:
    @staticmethod
    def listar(investigacion=None):
        return TipoDocumentoSelector.listar(investigacion=investigacion)

    @staticmethod
    def obtener(tipo_documento_id):
        return TipoDocumentoSelector.obtener(tipo_documento_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre_documento, grupo, investigacion=None, es_obligatorio=False, ejecutor=None):
        TipoDocumentoValidator.validar_creacion(nombre_documento, grupo, investigacion)
        tipo = TipoDocumento.objects.create(
            nombre_documento=nombre_documento.strip(),
            grupo=grupo.strip(),
            investigacion=investigacion,
            es_obligatorio=es_obligatorio,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el tipo de documento '{tipo.nombre_documento}' (grupo={tipo.grupo}, "
            f"investigacion={tipo.investigacion}, obligatorio={tipo.es_obligatorio}, id={tipo.pk}).",
            objeto=tipo,
        )
        return tipo

    @staticmethod
    @transaction.atomic
    def actualizar(tipo_documento_id, nombre_documento, grupo, investigacion=None, es_obligatorio=False, ejecutor=None):
        tipo_documento = TipoDocumentoSelector.obtener(tipo_documento_id)
        TipoDocumentoValidator.validar_actualizacion(tipo_documento_id, nombre_documento, grupo, investigacion)
        tipo_documento.nombre_documento = nombre_documento.strip()
        tipo_documento.grupo = grupo.strip()
        tipo_documento.investigacion = investigacion
        tipo_documento.es_obligatorio = es_obligatorio
        tipo_documento.save(update_fields=["nombre_documento", "grupo", "investigacion", "es_obligatorio"])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el tipo de documento a '{tipo_documento.nombre_documento}' (id={tipo_documento.pk}).",
            objeto=tipo_documento,
        )
        return tipo_documento

    @staticmethod
    def listar_por_grupo(grupo, investigacion=None):
        return TipoDocumentoSelector.listar_por_grupo(grupo, investigacion=investigacion)