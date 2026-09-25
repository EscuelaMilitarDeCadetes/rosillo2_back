from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.models import ParticipanteProceso
from apps.investigacion_formativa.selectors.participante_proceso_selector import (
    ParticipanteProcesoSelector,
)
from apps.investigacion_formativa.validators.participante_proceso_validator import (
    ParticipanteProcesoValidator,
)
from apps.investigacion_formativa.services._soporte import (
    ejecutor_es_facultad,
    notificar,
    usuario_id_de_persona,
)
from apps.common.services.historial_service import HistorialService
from apps.common.services.aprobacion_service import AprobacionService
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector

TIPO_DOCUMENTO_APROBACION_PARTICIPANTE = 'APROBACION_PARTICIPANTE'


class ParticipanteProcesoService:

    @staticmethod
    def listar():
        return ParticipanteProcesoSelector.listar()

    @staticmethod
    def obtener(participante_id):
        return ParticipanteProcesoSelector.obtener(participante_id)

    @staticmethod
    def listar_por_proceso(proceso_formativo_id):
        return ParticipanteProcesoSelector.listar_por_proceso(proceso_formativo_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_formativo_id, persona_id, rol_en_modalidad, ejecutor, fecha_finalizacion=None,
              usuario_revisor_id=None):
        """Crea la vinculación de inmediato. Si el ejecutor tiene rol Facultad,
        además abre una Aprobacion pendiente para que un Decano la revise
        después (supervisión posterior, no bloqueante) — requiere
        `usuario_revisor_id`."""
        ParticipanteProcesoValidator.validar_creacion(
            proceso_formativo_id, persona_id, rol_en_modalidad, fecha_finalizacion
        )

        es_facultad = ejecutor_es_facultad(ejecutor)
        if es_facultad and not usuario_revisor_id:
            raise ValidationError(
                {"usuario_revisor_id": "Debe indicar el Decano que revisará esta asignación."}
            )

        participante = ParticipanteProceso.objects.create(
            proceso_formativo_id=proceso_formativo_id,
            persona_id=persona_id,
            rol_en_modalidad=rol_en_modalidad,
            fecha_finalizacion=fecha_finalizacion,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se vinculó a '{participante.persona}' como '{rol_en_modalidad}' en el proceso "
            f"'{participante.proceso_formativo.titulo}' (id={participante.pk}).",
            objeto=participante,
        )

        # Notifica a la persona asignada (tutor/jurado/otro).
        notificar(
            usuario_id_de_persona(participante.persona),
            f"Fuiste asignado como '{rol_en_modalidad}' en el proceso de grado "
            f"'{participante.proceso_formativo.titulo}'.",
            tipo='info',
        )

        if es_facultad:
            tipo_documento = TipoDocumentoSelector.obtener_por_nombre(
                TIPO_DOCUMENTO_APROBACION_PARTICIPANTE
            )
            aprobacion = AprobacionService.crear(
                usuario_revisor_id=usuario_revisor_id,
                tipo_documento_id=tipo_documento.pk,
                id_documento=participante.pk,
                ejecutor=ejecutor,
                observacion=(
                    f"Asignación de '{participante.persona}' como '{rol_en_modalidad}' "
                    f"en '{participante.proceso_formativo.titulo}', a cargo de Facultad."
                ),
            )
            notificar(
                usuario_revisor_id,
                f"Facultad asignó a '{participante.persona}' como '{rol_en_modalidad}' en "
                f"'{participante.proceso_formativo.titulo}'. Pendiente de tu revisión "
                f"(aprobacion id={aprobacion.pk}).",
                tipo='info',
            )

        return participante

    @staticmethod
    @transaction.atomic
    def actualizar(participante_id, rol_en_modalidad, ejecutor, fecha_finalizacion=None):
        participante = ParticipanteProcesoSelector.obtener(participante_id)
        ParticipanteProcesoValidator.validar_actualizacion(
            participante, rol_en_modalidad, fecha_finalizacion
        )
        participante.rol_en_modalidad = rol_en_modalidad
        participante.fecha_finalizacion = fecha_finalizacion
        participante.save(update_fields=['rol_en_modalidad', 'fecha_finalizacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la participación de '{participante.persona}' (id={participante.pk}) "
            f"a rol '{rol_en_modalidad}'.",
            objeto=participante,
        )
        return participante

    @staticmethod
    @transaction.atomic
    def finalizar(participante_id, ejecutor):
        participante = ParticipanteProcesoSelector.obtener(participante_id)
        ParticipanteProcesoValidator.validar_finalizacion(participante)
        participante.fecha_finalizacion = timezone.now().date()
        participante.activo = False
        participante.save(update_fields=['fecha_finalizacion', 'activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se finalizó la participación de '{participante.persona}' en el proceso "
            f"'{participante.proceso_formativo.titulo}' (id={participante.pk}).",
            objeto=participante,
        )
        return participante

    @staticmethod
    @transaction.atomic
    def eliminar(participante_id, ejecutor):
        participante = ParticipanteProcesoSelector.obtener(participante_id)
        ParticipanteProcesoValidator.validar_eliminacion(participante)
        participante.activo = False
        participante.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) la participación de '{participante.persona}' "
            f"(id={participante.pk}).",
            objeto=participante,
        )
        return participante