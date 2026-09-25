from django.db import transaction

from apps.investigacion_formal.models import Ejecucion
from apps.investigacion_formal.selectors.ejecucion_selector import EjecucionSelector
from apps.investigacion_formal.selectors.monto_selector import MontoSelector
from apps.investigacion_formal.validators.ejecucion_validator import EjecucionValidator
from apps.common.services.historial_service import HistorialService


class EjecucionService:

    @staticmethod
    def listar():
        return EjecucionSelector.listar()

    @staticmethod
    def obtener(ejecucion_id):
        return EjecucionSelector.obtener(ejecucion_id)

    @staticmethod
    def listar_por_monto(monto_id, solo_activas=True):
        return EjecucionSelector.listar_por_monto(monto_id, solo_activas=solo_activas)

    @staticmethod
    @transaction.atomic
    def crear(monto_id, tipo_rubro_id, nombre, costo, descripcion, ejecutor):
        EjecucionValidator.validar_creacion(monto_id, tipo_rubro_id, nombre, costo, descripcion)

        ejecucion = Ejecucion.objects.create(
            monto_id=monto_id,
            tipo_rubro_id=tipo_rubro_id,
            nombre=nombre.strip(),
            costo=costo,
            descripcion=descripcion.strip(),
            estado=True,
        )

        monto = MontoSelector.obtener(monto_id)
        monto.ejecutado = (monto.ejecutado or 0) + costo
        monto.save(update_fields=['ejecutado'])

        HistorialService.registrar(
            ejecutor,
            f"Se registró la ejecución '{ejecucion.nombre}' por {costo} en el "
            f"proyecto '{monto.proyecto.titulo}' (id={ejecucion.pk}).",
            objeto=ejecucion,
        )
        return ejecucion

    @staticmethod
    @transaction.atomic
    def actualizar(ejecucion_id, ejecutor, monto_id=None, tipo_rubro_id=None,
                    nombre=None, costo=None, descripcion=None):
        ejecucion = EjecucionSelector.obtener(ejecucion_id)

        nuevo_monto_id = monto_id if monto_id is not None else ejecucion.monto_id
        nuevo_tipo_rubro_id = tipo_rubro_id if tipo_rubro_id is not None else ejecucion.tipo_rubro_id
        nuevo_nombre = nombre if nombre is not None else ejecucion.nombre
        nuevo_costo = costo if costo is not None else ejecucion.costo
        nueva_descripcion = descripcion if descripcion is not None else ejecucion.descripcion

        EjecucionValidator.validar_actualizacion(
            ejecucion, nuevo_monto_id, nuevo_tipo_rubro_id, nuevo_nombre, nuevo_costo, nueva_descripcion
        )
        
        cambia_monto = nuevo_monto_id != ejecucion.monto_id
        cambia_costo = nuevo_costo != ejecucion.costo
        costo_anterior = ejecucion.costo
        costo_nuevo = nuevo_costo
        
        if cambia_monto:
            monto_origen = MontoSelector.obtener(ejecucion.monto_id)
            monto_destino = MontoSelector.obtener(nuevo_monto_id)
            monto_origen.ejecutado = (
                monto_origen.ejecutado or 0
            ) - costo_anterior
            monto_destino.ejecutado = (
                monto_destino.ejecutado or 0
            ) + costo_nuevo
            monto_origen.save(update_fields=['ejecutado'])
            monto_destino.save(update_fields=['ejecutado'])
        elif cambia_costo:
            monto = MontoSelector.obtener(ejecucion.monto_id)
            monto.ejecutado = (
                monto.ejecutado or 0
            ) + (costo_nuevo - costo_anterior)
            monto.save(update_fields=['ejecutado'])

        ejecucion.monto_id = nuevo_monto_id
        ejecucion.tipo_rubro_id = nuevo_tipo_rubro_id
        ejecucion.nombre = nuevo_nombre.strip()
        ejecucion.costo = nuevo_costo
        ejecucion.descripcion = nueva_descripcion.strip()
        ejecucion.save(update_fields=['monto', 'tipo_rubro', 'nombre', 'costo', 'descripcion'])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la ejecución '{ejecucion.nombre}' (id={ejecucion.pk}).",
            objeto=ejecucion,
        )
        return ejecucion

    @staticmethod
    @transaction.atomic
    def eliminar(ejecucion_id, ejecutor):
        """Soft-delete: desactiva la ejecución y revierte su costo del monto ejecutado."""
        ejecucion = EjecucionSelector.obtener(ejecucion_id)
        EjecucionValidator.validar_eliminacion(ejecucion)

        monto = MontoSelector.obtener(ejecucion.monto_id)
        monto.ejecutado = (monto.ejecutado or 0) - ejecucion.costo
        monto.save(update_fields=['ejecutado'])

        ejecucion.estado = False
        ejecucion.save(update_fields=['estado'])

        HistorialService.registrar(
            ejecutor,
            f"Se desactivó la ejecución '{ejecucion.nombre}' (id={ejecucion.pk}) "
            f"y se revirtió su costo del monto ejecutado del proyecto "
            f"'{monto.proyecto.titulo}'.",
            objeto=ejecucion,
        )
        return ejecucion