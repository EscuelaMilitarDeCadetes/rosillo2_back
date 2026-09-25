from django.db import transaction

from apps.investigacion_formal.models import TipoCalificacion
from apps.investigacion_formal.selectors.tipo_calificacion_selector import TipoCalificacionSelector
from apps.investigacion_formal.validators.tipo_calificacion_validator import TipoCalificacionValidator
from apps.common.services.historial_service import HistorialService


class TipoCalificacionService:

    @staticmethod
    def listar():
        return TipoCalificacionSelector.listar()

    @staticmethod
    def obtener(tipo_calificacion_id):
        return TipoCalificacionSelector.obtener(tipo_calificacion_id)

    @staticmethod
    def listar_evaluables():
        return TipoCalificacionSelector.listar_evaluables()

    @staticmethod
    @transaction.atomic
    def crear(tipo_calificacion, descripcion, evaluacion, orden_fase, ejecutor):
        TipoCalificacionValidator.validar_creacion(
            tipo_calificacion, descripcion, evaluacion, orden_fase
        )
        fase = TipoCalificacion.objects.create(
            tipo_calificacion=tipo_calificacion.strip(),
            descripcion=descripcion.strip(),
            evaluacion=evaluacion,
            orden_fase=orden_fase,
        )
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se creó el tipo de calificación "
            f"'{fase.tipo_calificacion}' (orden={fase.orden_fase}, id={fase.pk}).",
            objeto=fase,
        )
        return fase

    @staticmethod
    @transaction.atomic
    def actualizar(tipo_calificacion_id, tipo_calificacion, descripcion, evaluacion, orden_fase, ejecutor):
        fase = TipoCalificacionSelector.obtener(tipo_calificacion_id)
        TipoCalificacionValidator.validar_actualizacion(
            tipo_calificacion_id, tipo_calificacion, descripcion, evaluacion, orden_fase
        )
        fase.tipo_calificacion = tipo_calificacion.strip()
        fase.descripcion = descripcion.strip()
        fase.evaluacion = evaluacion
        fase.orden_fase = orden_fase
        fase.save(update_fields=['tipo_calificacion', 'descripcion', 'evaluacion', 'orden_fase'])
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se actualizó el tipo de calificación "
            f"'{fase.tipo_calificacion}' (id={fase.pk}).",
            objeto=fase,
        )
        return fase