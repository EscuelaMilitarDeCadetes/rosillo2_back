from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.investigacion_formativa.models import Homologacion
from apps.investigacion_formativa.selectors.homologacion_selector import HomologacionSelector
from apps.investigacion_formativa.validators.homologacion_validator import HomologacionValidator
from apps.common.services.historial_service import HistorialService
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)
from apps.investigacion_formativa.services._soporte import (
    notificar,
    usuario_id_estudiante_de_proceso,
    validar_ejecutor_autor_o_gestor_por_proceso,
)


class HomologacionService:

    @staticmethod
    def listar():
        return HomologacionSelector.listar()

    @staticmethod
    def obtener(homologacion_id):
        return HomologacionSelector.obtener(homologacion_id)

    @staticmethod
    def obtener_por_proceso(proceso_id):
        return HomologacionSelector.obtener_por_proceso(proceso_id)

    @staticmethod
    def listar_pendientes():
        return HomologacionSelector.listar_pendientes()

    @staticmethod
    @transaction.atomic
    def crear(proceso_id, ejecutor, observaciones=None):
        HomologacionValidator.validar_creacion(proceso_id, observaciones)        
        # El estudiante solo puede abrir la homologación de SU propio
        # proceso; Facultad/Decano pueden hacerlo en su nombre.
        proceso = ProcesoFormativoSelector.obtener(proceso_id)
        validar_ejecutor_autor_o_gestor_por_proceso(
            proceso, ejecutor, "esta homologación"
        )
        homologacion = Homologacion.objects.create(
            proceso_id=proceso_id,
            observaciones=observaciones,
            estado='PENDIENTE',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se abrió una solicitud de homologación para el proceso "
            f"'{homologacion.proceso.titulo}' (id={homologacion.pk}).",
            objeto=homologacion,
        )
        return homologacion

    @staticmethod
    @transaction.atomic
    def aprobar(homologacion_id, aprobado_por_id, creditos_reconocidos, ejecutor, acta_homologacion_id=None):
        # Sin cambios: acción exclusiva de Facultad/Decano.
        homologacion = HomologacionSelector.obtener(homologacion_id)
        HomologacionValidator.validar_aprobacion(
            homologacion, aprobado_por_id, creditos_reconocidos, acta_homologacion_id
        )
        homologacion.estado = 'APROBADA'
        homologacion.aprobado_por_id = aprobado_por_id
        homologacion.creditos_reconocidos = creditos_reconocidos
        homologacion.acta_homologacion_id = acta_homologacion_id
        homologacion.fecha_homologacion = timezone.now().date()
        homologacion.save(update_fields=[
            'estado', 'aprobado_por', 'creditos_reconocidos', 'acta_homologacion', 'fecha_homologacion',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se aprobó la homologación del proceso '{homologacion.proceso.titulo}' "
            f"({creditos_reconocidos} créditos reconocidos, id={homologacion.pk}).",
            objeto=homologacion,
        )
        notificar(
            usuario_id_estudiante_de_proceso(homologacion.proceso),
            f"Tu homologación del proceso '{homologacion.proceso.titulo}' fue aprobada "
            f"({creditos_reconocidos} créditos reconocidos).",
            tipo='exito',
        )
        return homologacion

    @staticmethod
    @transaction.atomic
    def cargar_acta(homologacion_id, acta_homologacion_id, ejecutor):
        # Sin cambios: acción exclusiva de Facultad/Decano.
        homologacion = HomologacionSelector.obtener(homologacion_id)
        if homologacion.estado != 'APROBADA':
            raise ValidationError(
                "Solo se puede cargar el acta de una homologación en estado 'APROBADA'."
            )
        homologacion.acta_homologacion_id = acta_homologacion_id
        homologacion.save(update_fields=['acta_homologacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se cargó el acta de homologación del proceso '{homologacion.proceso.titulo}' "
            f"(id={homologacion.pk}).",
            objeto=homologacion,
        )
        return homologacion

    @staticmethod
    @transaction.atomic
    def rechazar(homologacion_id, observaciones, ejecutor):
        # Sin cambios: acción exclusiva de Facultad/Decano.
        homologacion = HomologacionSelector.obtener(homologacion_id)
        HomologacionValidator.validar_rechazo(homologacion, observaciones)
        homologacion.estado = 'RECHAZADA'
        homologacion.observaciones = observaciones
        homologacion.save(update_fields=['estado', 'observaciones'])
        HistorialService.registrar(
            ejecutor,
            f"Se rechazó la homologación del proceso '{homologacion.proceso.titulo}' "
            f"(id={homologacion.pk}): {observaciones}",
            objeto=homologacion,
        )
        notificar(
            usuario_id_estudiante_de_proceso(homologacion.proceso),
            f"Tu homologación del proceso '{homologacion.proceso.titulo}' fue rechazada. "
            f"Motivo: {observaciones}",
            tipo='alerta',
        )
        return homologacion