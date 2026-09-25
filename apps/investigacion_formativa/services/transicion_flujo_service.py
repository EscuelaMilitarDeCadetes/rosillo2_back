# apps/investigacion_formativa/services/transicion_flujo_service.py
from django.db import transaction

from apps.investigacion_formativa.models import TransicionFlujo
from apps.investigacion_formativa.selectors.transicion_flujo_selector import (
    TransicionFlujoSelector,
)
from apps.investigacion_formativa.validators.transicion_flujo_validator import (
    TransicionFlujoValidator,
)
from apps.common.services.historial_service import HistorialService


class TransicionFlujoService:

    @staticmethod
    def listar():
        return TransicionFlujoSelector.listar()

    @staticmethod
    def obtener(transicion_id):
        return TransicionFlujoSelector.obtener(transicion_id)

    @staticmethod
    def listar_por_etapa_origen(etapa_origen_id):
        return TransicionFlujoSelector.listar_por_etapa_origen(etapa_origen_id)

    @staticmethod
    @transaction.atomic
    def crear(etapa_origen_id, etapa_destino_id, nombre, ejecutor,
              condicion=None, accion_automatica=None, orden=0):
        TransicionFlujoValidator.validar_creacion(
            etapa_origen_id, etapa_destino_id, nombre, condicion, accion_automatica, orden
        )
        transicion = TransicionFlujo.objects.create(
            etapa_origen_id=etapa_origen_id,
            etapa_destino_id=etapa_destino_id,
            nombre=nombre,
            condicion=condicion,
            accion_automatica=accion_automatica,
            orden=orden,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó la transición '{transicion.nombre}' entre "
            f"'{transicion.etapa_origen.nombre}' y '{transicion.etapa_destino.nombre}' "
            f"(id={transicion.pk}).",
            objeto=transicion,
        )
        return transicion

    @staticmethod
    @transaction.atomic
    def actualizar(transicion_id, etapa_origen_id, etapa_destino_id, nombre, ejecutor,
                    condicion=None, accion_automatica=None, orden=0):
        transicion = TransicionFlujoSelector.obtener(transicion_id)
        TransicionFlujoValidator.validar_actualizacion(
            transicion, etapa_origen_id, etapa_destino_id, nombre, condicion, accion_automatica, orden
        )
        transicion.etapa_origen_id = etapa_origen_id
        transicion.etapa_destino_id = etapa_destino_id
        transicion.nombre = nombre
        transicion.condicion = condicion
        transicion.accion_automatica = accion_automatica
        transicion.orden = orden
        transicion.save(update_fields=[
            'etapa_origen', 'etapa_destino', 'nombre', 'condicion', 'accion_automatica', 'orden',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la transición '{transicion.nombre}' (id={transicion.pk}).",
            objeto=transicion,
        )
        return transicion

    @staticmethod
    @transaction.atomic
    def activar(transicion_id, ejecutor):
        transicion = TransicionFlujoSelector.obtener(transicion_id)
        TransicionFlujoValidator.validar_activacion(transicion)
        transicion.activo = True
        transicion.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se activó la transición '{transicion.nombre}' (id={transicion.pk}).",
            objeto=transicion,
        )
        return transicion

    @staticmethod
    @transaction.atomic
    def desactivar(transicion_id, ejecutor):
        transicion = TransicionFlujoSelector.obtener(transicion_id)
        TransicionFlujoValidator.validar_desactivacion(transicion)
        transicion.activo = False
        transicion.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó la transición '{transicion.nombre}' (id={transicion.pk}).",
            objeto=transicion,
        )
        return transicion