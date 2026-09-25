from django.db import transaction

from apps.common.services.tarea_service import TareaService
from apps.investigacion_formal.models import Calificacion
from apps.investigacion_formal.selectors.calificacion_selector import CalificacionSelector
from apps.investigacion_formal.validators.calificacion_validator import CalificacionValidator
from apps.common.services.historial_service import HistorialService
from apps.common.services.notificacion_service import NotificacionService 


class CalificacionService:

    @staticmethod
    def listar():
        return CalificacionSelector.listar()

    @staticmethod
    def obtener(calificacion_id):
        return CalificacionSelector.obtener(calificacion_id)

    @staticmethod
    def listar_por_proyecto_x_convocatoria(aplicar_id):
        return CalificacionSelector.listar_por_proyecto_x_convocatoria(aplicar_id)

    @staticmethod
    @transaction.atomic
    def crear(fase_id, aplicar_id, ejecutor, observacion=''):
        CalificacionValidator.validar_creacion(fase_id, aplicar_id, observacion)
        es_primera_fase = not CalificacionSelector.listar_por_proyecto_x_convocatoria(
            aplicar_id
        ).exists()
        calificacion = Calificacion.objects.create(
            fase_id=fase_id,
            aplicar_id=aplicar_id,
            observacion=observacion or '',
            aprobado=False,
            primer_sin_observacion=es_primera_fase,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el registro de calificación para la fase id={fase_id} "
            f"del proyecto-convocatoria id={aplicar_id} (id={calificacion.pk}).",
            objeto=calificacion,
        )
        return calificacion

    @staticmethod
    @transaction.atomic
    def calificar_fase(calificacion_id, aprobado, observacion, ejecutor):
        """Réplica de CalificarControlador.ejecutarCalificionFase: registra el
        resultado de la fase, habilita la siguiente fase (primer_sin_observacion)
        y actualiza el estado agregado del ProyectoXConvocatoria.
        CORREGIDO (INV-08): además del Historial, ahora notifica al
        investigador responsable del proyecto (Notificacion interna + correo),
        igual que hacía el envío de correo del Thymeleaf original al calificar
        una fase.
        """
        calificacion = CalificacionSelector.obtener(calificacion_id)
        CalificacionValidator.validar_calificacion(observacion, aprobado)
        calificacion.aprobado = aprobado
        calificacion.observacion = observacion or ''
        calificacion.primer_sin_observacion = False
        calificacion.save(update_fields=['aprobado', 'observacion', 'primer_sin_observacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se calificó la fase '{calificacion.fase.tipo_calificacion}' del proyecto "
            f"'{calificacion.aplicar.proyecto.titulo}' como "
            f"{'APROBADO' if aprobado else 'NO APROBADO'} (id={calificacion.pk}).",
            objeto=calificacion,
        )
        aplicar = calificacion.aplicar
        proyecto = aplicar.proyecto
        destinatario_id = proyecto.usuario_id
        nombre_fase = calificacion.fase.tipo_calificacion
        if not aprobado:
            aplicar.ultimo_filtro_calificacion = calificacion.fase.descripcion
            aplicar.calificacion_ultimo_filtro_calificacion = 'NO_APROBADO'
            aplicar.estado_finalizado_calificacion = True
            aplicar.save(update_fields=[
                'ultimo_filtro_calificacion',
                'calificacion_ultimo_filtro_calificacion',
                'estado_finalizado_calificacion',
            ])
            proyecto.estado_aprobado = 'NO_APROBADO'
            proyecto.save(update_fields=['estado_aprobado'])
            NotificacionService.crear(
                usuario_destino_id=destinatario_id,
                mensaje=(
                    f"Su proyecto '{proyecto.titulo}' NO fue aprobado en la fase "
                    f"'{nombre_fase}'. Observación: {calificacion.observacion or 'sin observación'}."
                ),
                tipo='error',
                url_relacionada=f"/investigacion-formal/proyectos/{proyecto.pk}",
                notificar_email=True,
            )
        else:
            aplicar.ultimo_filtro_calificacion = calificacion.fase.descripcion
            aplicar.calificacion_ultimo_filtro_calificacion = 'APROBADO'
            siguiente = CalificacionSelector.listar_por_proyecto_x_convocatoria(
                aplicar.pk
            ).filter(fase__orden_fase__gt=calificacion.fase.orden_fase).order_by(
                'fase__orden_fase'
            ).first()
            if siguiente is not None and not siguiente.observacion:
                siguiente.primer_sin_observacion = True
                siguiente.save(update_fields=['primer_sin_observacion'])
            todas_calificadas = CalificacionSelector.contar_fases_calificadas(
                aplicar.pk
            ) == CalificacionSelector.listar_por_proyecto_x_convocatoria(aplicar.pk).count()
            if todas_calificadas:
                aplicar.estado_finalizado_calificacion = True
                proyecto.estado_aprobado = 'APROBADO'
                proyecto.save(update_fields=['estado_aprobado'])
                NotificacionService.crear(
                    usuario_destino_id=destinatario_id,
                    mensaje=(
                        f"¡Su proyecto '{proyecto.titulo}' fue APROBADO en todas las fases "
                        f"de calificación!"
                    ),
                    tipo='exito',
                    url_relacionada=f"/investigacion-formal/proyectos/{proyecto.pk}",
                    notificar_email=True,
                )
                TareaService.crear_recordatorio(
                    usuario_id=ejecutor.pk,
                    descripcion=(
                        f"Asignar fecha de inicio y fin al proyecto aprobado "
                        f"'{proyecto.titulo}'"
                    ),
                    objeto=proyecto,
                    ejecutor=ejecutor,
                )
            else:
                NotificacionService.crear(
                    usuario_destino_id=destinatario_id,
                    mensaje=(
                        f"Su proyecto '{proyecto.titulo}' aprobó la fase '{nombre_fase}'. "
                        f"Continúa a la siguiente fase de calificación."
                    ),
                    tipo='info',
                    url_relacionada=f"/investigacion-formal/proyectos/{proyecto.pk}",
                    notificar_email=True,
                )
            aplicar.save(update_fields=[
                'ultimo_filtro_calificacion',
                'calificacion_ultimo_filtro_calificacion',
                'estado_finalizado_calificacion',
            ])
        return calificacion