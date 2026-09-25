from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.models import EventoEvaluativo
from apps.investigacion_formativa.selectors.evento_evaluativo_selector import (
    EventoEvaluativoSelector,
)
from apps.investigacion_formativa.validators.evento_evaluativo_validator import (
    EventoEvaluativoValidator,
)
from apps.investigacion_formativa.services._soporte import (
    ejecutor_es_facultad,
    notificar_varios,
    usuarios_ids_participantes_de_proceso,
)
from apps.common.services.historial_service import HistorialService
from apps.common.services.aprobacion_service import AprobacionService
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector

TIPO_DOCUMENTO_APROBACION_EVENTO_EVALUATIVO = 'APROBACION_EVENTO_EVALUATIVO'
ROLES_A_NOTIFICAR_SUSTENTACION = ['ESTUDIANTE', 'TUTOR', 'JURADO']


class EventoEvaluativoService:

    @staticmethod
    def listar():
        return EventoEvaluativoSelector.listar()

    @staticmethod
    def obtener(evento_id):
        return EventoEvaluativoSelector.obtener(evento_id)

    @staticmethod
    def listar_por_proceso(proceso_formativo_id):
        return EventoEvaluativoSelector.listar_por_proceso(proceso_formativo_id)
    
    @staticmethod
    def listar_proximas(proceso_formativo_id=None):
        return EventoEvaluativoSelector.listar_proximas(proceso_formativo_id=proceso_formativo_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_formativo_id, numero, es_obligatoria, fecha_sustentacion, lugar, ejecutor,
              usuario_revisor_id=None):
        """Programa la sustentación de inmediato y notifica a estudiante, tutor
        y jurados del proceso. Si el ejecutor tiene rol Facultad, además abre
        una Aprobacion pendiente para que un Decano la revise (supervisión
        posterior, no bloqueante) — requiere `usuario_revisor_id`."""
        EventoEvaluativoValidator.validar_creacion(
            proceso_formativo_id, numero, es_obligatoria, fecha_sustentacion, lugar
        )
        es_facultad = ejecutor_es_facultad(ejecutor)
        if es_facultad and not usuario_revisor_id:
            raise ValidationError(
                {"usuario_revisor_id": "Debe indicar el Decano que revisará esta sustentación."}
            )
        evento = EventoEvaluativo.objects.create(
            proceso_formativo_id=proceso_formativo_id,
            numero=numero,
            es_obligatoria=es_obligatoria,
            fecha_sustentacion=fecha_sustentacion,
            lugar=lugar,
            resultado='PENDIENTE',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se programó la sustentación #{numero} del proceso "
            f"'{evento.proceso_formativo.titulo}' para el {fecha_sustentacion} (id={evento.pk}).",
            objeto=evento,
        )
        notificar_varios(
            usuarios_ids_participantes_de_proceso(evento.proceso_formativo, ROLES_A_NOTIFICAR_SUSTENTACION),
            f"Se programó la sustentación #{numero} del proceso "
            f"'{evento.proceso_formativo.titulo}' para el {fecha_sustentacion} en '{lugar}'.",
            tipo='info',
        )
        if es_facultad:
            tipo_documento = TipoDocumentoSelector.obtener_por_nombre(
                TIPO_DOCUMENTO_APROBACION_EVENTO_EVALUATIVO
            )
            aprobacion = AprobacionService.crear(
                usuario_revisor_id=usuario_revisor_id,
                tipo_documento_id=tipo_documento.pk,
                id_documento=evento.pk,
                ejecutor=ejecutor,
                observacion=(
                    f"Sustentación #{numero} del proceso '{evento.proceso_formativo.titulo}' "
                    f"programada por Facultad para el {fecha_sustentacion}."
                ),
            )
            notificar_varios(
                [usuario_revisor_id],
                f"Facultad programó la sustentación #{numero} de "
                f"'{evento.proceso_formativo.titulo}'. Pendiente de tu revisión "
                f"(aprobacion id={aprobacion.pk}).",
                tipo='info',
            )
        return evento
    
    @staticmethod
    @transaction.atomic
    def cargar_acta(evento_id, acta_sustentacion_id, ejecutor):
        """Carga el acta sobre un evento que YA tiene resultado registrado
        (ver EventoEvaluativoValidator.validar_registro_resultado, que exige
        que el resultado siga siendo 'PENDIENTE' — aquí exigimos lo contrario)."""
        evento = EventoEvaluativoSelector.obtener(evento_id)
        if not evento.resultado or evento.resultado == 'PENDIENTE':
            raise ValidationError(
                "Debe registrar el resultado de la sustentación antes de cargar el acta."
            )
        if evento.acta_sustentacion_id is not None:
            raise ValidationError("Este evento evaluativo ya tiene un acta de sustentación cargada.")
        evento.acta_sustentacion_id = acta_sustentacion_id
        evento.save(update_fields=['acta_sustentacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se cargó el acta de sustentación del proceso '{evento.proceso_formativo.titulo}' "
            f"(id={evento.pk}).",
            objeto=evento,
        )
        return evento

    @staticmethod
    @transaction.atomic
    def reprogramar(evento_id, fecha_sustentacion, lugar, ejecutor):
        evento = EventoEvaluativoSelector.obtener(evento_id)
        EventoEvaluativoValidator.validar_reprogramacion(evento, fecha_sustentacion, lugar)
        evento.fecha_sustentacion = fecha_sustentacion
        evento.lugar = lugar
        evento.save(update_fields=['fecha_sustentacion', 'lugar'])
        HistorialService.registrar(
            ejecutor,
            f"Se reprogramó la sustentación (id={evento.pk}) del proceso "
            f"'{evento.proceso_formativo.titulo}' para el {fecha_sustentacion} en '{lugar}'.",
            objeto=evento,
        )
        notificar_varios(
            usuarios_ids_participantes_de_proceso(evento.proceso_formativo, ROLES_A_NOTIFICAR_SUSTENTACION),
            f"La sustentación del proceso '{evento.proceso_formativo.titulo}' se reprogramó "
            f"para el {fecha_sustentacion} en '{lugar}'.",
            tipo='alerta',
        )
        return evento

    @staticmethod
    @transaction.atomic
    def registrar_resultado(evento_id, resultado, ejecutor, acta_sustentacion_id=None):
        evento = EventoEvaluativoSelector.obtener(evento_id)
        EventoEvaluativoValidator.validar_registro_resultado(evento, resultado, acta_sustentacion_id)
        evento.resultado = resultado
        evento.acta_sustentacion_id = acta_sustentacion_id
        evento.save(update_fields=['resultado', 'acta_sustentacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se registró el resultado '{resultado}' de la sustentación (id={evento.pk}) "
            f"del proceso '{evento.proceso_formativo.titulo}'.",
            objeto=evento,
        )
        notificar_varios(
            usuarios_ids_participantes_de_proceso(evento.proceso_formativo, ROLES_A_NOTIFICAR_SUSTENTACION),
            f"Se registró el resultado de la sustentación de "
            f"'{evento.proceso_formativo.titulo}': {resultado}.",
            tipo='info',
        )
        return evento

    @staticmethod
    @transaction.atomic
    def eliminar(evento_id, ejecutor):
        evento = EventoEvaluativoSelector.obtener(evento_id)
        EventoEvaluativoValidator.validar_eliminacion(evento)
        evento.activo = False
        evento.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó la sustentación #{evento.numero} del proceso "
            f"'{evento.proceso_formativo.titulo}' (id={evento.pk}).",
            objeto=evento,
        )
        return evento