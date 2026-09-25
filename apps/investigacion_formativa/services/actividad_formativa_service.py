from django.db import transaction
from apps.investigacion_formativa.models import ActividadFormativa
from apps.investigacion_formativa.selectors.actividad_formativa_selector import (
    ActividadFormativaSelector,
)
from apps.investigacion_formativa.validators.actividad_formativa_validator import (
    ActividadFormativaValidator,
)
from apps.common.services.historial_service import HistorialService
from apps.investigacion_formativa.services._soporte import validar_ejecutor_autor_o_gestor


class ActividadFormativaService:

    @staticmethod
    def listar():
        return ActividadFormativaSelector.listar()

    @staticmethod
    def obtener(actividad_id):
        return ActividadFormativaSelector.obtener(actividad_id)

    @staticmethod
    def listar_por_proceso(proceso_formativo_id):
        return ActividadFormativaSelector.listar_por_proceso(proceso_formativo_id)

    @staticmethod
    def listar_por_responsable(responsable_id):
        return ActividadFormativaSelector.listar_por_responsable(responsable_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_formativo_id, responsable_id, nombre, ejecutor, descripcion=None,
              fecha_inicio=None, fecha_fin=None, horas_dedicadas=None):
        ActividadFormativaValidator.validar_creacion(
            proceso_formativo_id, responsable_id, nombre, descripcion,
            fecha_inicio, fecha_fin, horas_dedicadas,
        )
        # Un estudiante solo puede reportar actividades de las que ÉL es
        # responsable; Facultad/Decano/Soporte pueden registrar en nombre
        # de cualquiera.
        validar_ejecutor_autor_o_gestor(responsable_id, ejecutor, "esta actividad formativa")
        actividad = ActividadFormativa.objects.create(
            proceso_formativo_id=proceso_formativo_id,
            responsable_id=responsable_id,
            nombre=nombre,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            horas_dedicadas=horas_dedicadas,
            estado='PLANIFICADA',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se planificó la actividad '{actividad.nombre}' del proceso "
            f"'{actividad.proceso_formativo.titulo}' (id={actividad.pk}).",
            objeto=actividad,
        )
        return actividad

    @staticmethod
    @transaction.atomic
    def actualizar(actividad_id, nombre, ejecutor, descripcion=None, fecha_inicio=None,
                    fecha_fin=None, horas_dedicadas=None):
        actividad = ActividadFormativaSelector.obtener(actividad_id)
        validar_ejecutor_autor_o_gestor(actividad.responsable_id, ejecutor, "esta actividad formativa")
        ActividadFormativaValidator.validar_actualizacion(
            actividad, nombre, descripcion, fecha_inicio, fecha_fin, horas_dedicadas
        )
        actividad.nombre = nombre
        actividad.descripcion = descripcion
        actividad.fecha_inicio = fecha_inicio
        actividad.fecha_fin = fecha_fin
        actividad.horas_dedicadas = horas_dedicadas
        actividad.save(update_fields=[
            'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'horas_dedicadas',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la actividad '{actividad.nombre}' (id={actividad.pk}).",
            objeto=actividad,
        )
        return actividad

    @staticmethod
    @transaction.atomic
    def iniciar(actividad_id, ejecutor):
        actividad = ActividadFormativaSelector.obtener(actividad_id)
        validar_ejecutor_autor_o_gestor(actividad.responsable_id, ejecutor, "esta actividad formativa")
        ActividadFormativaValidator.validar_inicio(actividad)
        actividad.estado = 'EN_PROGRESO'
        actividad.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se inició la actividad '{actividad.nombre}' (id={actividad.pk}).",
            objeto=actividad,
        )
        return actividad

    @staticmethod
    @transaction.atomic
    def completar(actividad_id, ejecutor, documento_soporte_id=None):
        actividad = ActividadFormativaSelector.obtener(actividad_id)
        validar_ejecutor_autor_o_gestor(actividad.responsable_id, ejecutor, "esta actividad formativa")
        ActividadFormativaValidator.validar_completado(actividad, documento_soporte_id)
        actividad.estado = 'COMPLETADA'
        actividad.documento_soporte_id = documento_soporte_id
        actividad.save(update_fields=['estado', 'documento_soporte'])
        HistorialService.registrar(
            ejecutor,
            f"Se completó la actividad '{actividad.nombre}' del proceso "
            f"'{actividad.proceso_formativo.titulo}' (id={actividad.pk}).",
            objeto=actividad,
        )
        return actividad

    @staticmethod
    @transaction.atomic
    def cancelar(actividad_id, ejecutor):
        actividad = ActividadFormativaSelector.obtener(actividad_id)
        validar_ejecutor_autor_o_gestor(actividad.responsable_id, ejecutor, "esta actividad formativa")
        ActividadFormativaValidator.validar_cancelacion(actividad)
        actividad.estado = 'CANCELADA'
        actividad.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se canceló la actividad '{actividad.nombre}' (id={actividad.pk}).",
            objeto=actividad,
        )
        return actividad

    @staticmethod
    @transaction.atomic
    def eliminar(actividad_id, ejecutor):
        actividad = ActividadFormativaSelector.obtener(actividad_id)
        validar_ejecutor_autor_o_gestor(actividad.responsable_id, ejecutor, "esta actividad formativa")
        ActividadFormativaValidator.validar_eliminacion(actividad)
        actividad.estado = 'ELIMINADA'
        actividad.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó la actividad formativa '{actividad.nombre}' (id={actividad.pk}).",
            objeto=actividad,
        )
        return actividad