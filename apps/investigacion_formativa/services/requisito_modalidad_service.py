from django.db import transaction

from apps.investigacion_formativa.models import RequisitoModalidad
from apps.investigacion_formativa.selectors.requisito_modalidad_selector import (
    RequisitoModalidadSelector,
)
from apps.investigacion_formativa.validators.requisito_modalidad_validator import (
    RequisitoModalidadValidator,
)
from apps.common.services.historial_service import HistorialService


class RequisitoModalidadService:

    @staticmethod
    def listar():
        return RequisitoModalidadSelector.listar()

    @staticmethod
    def obtener(requisito_id):
        return RequisitoModalidadSelector.obtener(requisito_id)

    @staticmethod
    def listar_activos_por_modalidad(modalidad_id):
        return RequisitoModalidadSelector.listar_activos_por_modalidad(modalidad_id)

    @staticmethod
    @transaction.atomic
    def crear(modalidad_id, tipo, descripcion, ejecutor, valor_numerico=None, valor_booleano=None):
        RequisitoModalidadValidator.validar_creacion(
            modalidad_id, tipo, descripcion, valor_numerico, valor_booleano
        )
        requisito = RequisitoModalidad.objects.create(
            modalidad_id=modalidad_id,
            tipo=tipo,
            descripcion=descripcion,
            valor_numerico=valor_numerico,
            valor_booleano=valor_booleano,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el requisito '{tipo}' para la modalidad "
            f"'{requisito.modalidad.nombre}' (id={requisito.pk}).",
            objeto=requisito,
        )
        return requisito

    @staticmethod
    @transaction.atomic
    def actualizar(requisito_id, tipo, descripcion, ejecutor, valor_numerico=None, valor_booleano=None):
        requisito = RequisitoModalidadSelector.obtener(requisito_id)
        RequisitoModalidadValidator.validar_actualizacion(
            requisito, tipo, descripcion, valor_numerico, valor_booleano
        )
        requisito.tipo = tipo
        requisito.descripcion = descripcion
        requisito.valor_numerico = valor_numerico
        requisito.valor_booleano = valor_booleano
        requisito.save(update_fields=['tipo', 'descripcion', 'valor_numerico', 'valor_booleano'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el requisito '{requisito.tipo}' de la modalidad "
            f"'{requisito.modalidad.nombre}' (id={requisito.pk}).",
            objeto=requisito,
        )
        return requisito

    @staticmethod
    @transaction.atomic
    def eliminar(requisito_id, ejecutor):
        requisito = RequisitoModalidadSelector.obtener(requisito_id)
        RequisitoModalidadValidator.validar_eliminacion(requisito)
        requisito.activo = False
        requisito.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) el requisito '{requisito.tipo}' de la modalidad "
            f"'{requisito.modalidad.nombre}' (id={requisito.pk}).",
            objeto=requisito,
        )
        return requisito