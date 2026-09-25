from django.db import transaction

from apps.investigacion_formativa.models import FlujoProceso
from apps.investigacion_formativa.selectors.flujo_proceso_selector import FlujoProcesoSelector
from apps.investigacion_formativa.validators.flujo_proceso_validator import FlujoProcesoValidator
from apps.common.services.historial_service import HistorialService


class FlujoProcesoService:

    @staticmethod
    def listar():
        return FlujoProcesoSelector.listar()

    @staticmethod
    def obtener(flujo_id):
        return FlujoProcesoSelector.obtener(flujo_id)

    @staticmethod
    def listar_activos():
        return FlujoProcesoSelector.listar_activos()
    
    @staticmethod
    def listar_por_modalidad(modalidad_id, activo=None):
        return FlujoProcesoSelector.listar_por_modalidad(modalidad_id, activo=activo)

    @staticmethod
    def obtener_version_vigente(modalidad_id):
        return FlujoProcesoSelector.obtener_version_vigente(modalidad_id)

    @staticmethod
    @transaction.atomic
    def crear(modalidad_id, nombre, fecha_vigencia_inicio, ejecutor, version=1,
              tipo='FORMATIVA', descripcion=None, fecha_vigencia_fin=None):
        FlujoProcesoValidator.validar_creacion(
            modalidad_id, nombre, fecha_vigencia_inicio, version, tipo, descripcion, fecha_vigencia_fin
        )
        flujo = FlujoProceso.objects.create(
            modalidad_id=modalidad_id,
            nombre=nombre,
            version=version,
            tipo=tipo,
            descripcion=descripcion,
            fecha_vigencia_inicio=fecha_vigencia_inicio,
            fecha_vigencia_fin=fecha_vigencia_fin,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el flujo '{flujo.nombre}' v{flujo.version} para la modalidad "
            f"'{flujo.modalidad.nombre}' (id={flujo.pk}).",
            objeto=flujo,
        )
        return flujo

    @staticmethod
    @transaction.atomic
    def actualizar(flujo_id, nombre, fecha_vigencia_inicio, ejecutor,
                    descripcion=None, fecha_vigencia_fin=None):
        flujo = FlujoProcesoSelector.obtener(flujo_id)
        FlujoProcesoValidator.validar_actualizacion(
            flujo, nombre, fecha_vigencia_inicio, descripcion, fecha_vigencia_fin
        )
        flujo.nombre = nombre
        flujo.fecha_vigencia_inicio = fecha_vigencia_inicio
        flujo.descripcion = descripcion
        flujo.fecha_vigencia_fin = fecha_vigencia_fin
        flujo.save(update_fields=[
            'nombre', 'fecha_vigencia_inicio', 'descripcion', 'fecha_vigencia_fin',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el flujo '{flujo.nombre}' v{flujo.version} (id={flujo.pk}).",
            objeto=flujo,
        )
        return flujo

    @staticmethod
    @transaction.atomic
    def activar(flujo_id, ejecutor):
        flujo = FlujoProcesoSelector.obtener(flujo_id)
        FlujoProcesoValidator.validar_activacion(flujo)
        flujo.activo = True
        flujo.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se activó el flujo '{flujo.nombre}' v{flujo.version} (id={flujo.pk}).",
            objeto=flujo,
        )
        return flujo

    @staticmethod
    @transaction.atomic
    def eliminar(flujo_id, ejecutor):
        flujo = FlujoProcesoSelector.obtener(flujo_id)
        FlujoProcesoValidator.validar_eliminacion(flujo)
        flujo.activo = False
        flujo.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) el flujo '{flujo.nombre}' v{flujo.version} (id={flujo.pk}).",
            objeto=flujo,
        )
        return flujo