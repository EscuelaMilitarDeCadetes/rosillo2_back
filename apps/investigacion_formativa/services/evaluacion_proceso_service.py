from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.models import EvaluacionProceso
from apps.investigacion_formativa.selectors.evaluacion_proceso_selector import (
    EvaluacionProcesoSelector,
)
from apps.investigacion_formativa.validators.evaluacion_proceso_validator import (
    EvaluacionProcesoValidator,
)
from apps.investigacion_formativa.services._soporte import (
    ejecutor_es_facultad,
    notificar,
    usuario_id_estudiante_de_proceso,
)
from apps.common.services.historial_service import HistorialService
from apps.common.services.aprobacion_service import AprobacionService
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector

TIPO_DOCUMENTO_APROBACION_EVALUACION_PROCESO = 'APROBACION_EVALUACION_PROCESO'


class EvaluacionProcesoService:
    """Append-only: a diferencia de Calificacion en investigacion_formal (que separa
    crear() de calificar_fase()), aquí el modelo exige aprobado/nota/resultado
    completos desde la creación (son BooleanField/FloatField/CharField sin default).
    No se expone actualizar() ni eliminar(): una evaluación ya emitida es un
    registro de auditoría académica y corregirla exige una nueva evaluación,
    no editar la anterior (misma razón que RevisionService)."""

    @staticmethod
    def listar():
        return EvaluacionProcesoSelector.listar()

    @staticmethod
    def obtener(evaluacion_id):
        return EvaluacionProcesoSelector.obtener(evaluacion_id)

    @staticmethod
    def listar_por_instancia_etapa(instancia_etapa_id):
        return EvaluacionProcesoSelector.listar_por_instancia_etapa(instancia_etapa_id)
    
    @staticmethod
    def listar_por_proceso(proceso_id):
        return EvaluacionProcesoSelector.listar_por_proceso(proceso_id)
    
    @staticmethod
    def listar_terceros_evaluadores(instancia_etapa_id):
        return EvaluacionProcesoSelector.listar_terceros_evaluadores(instancia_etapa_id)

    @staticmethod
    @transaction.atomic
    def crear(evaluador_id, instancia_etapa_id, concepto, aprobado, nota, tipo_evaluador,
              tipo_evaluacion, peso, resultado, ejecutor, es_tercer_evaluador=False,
              observaciones=None, rubrica_evaluacion='', criterio_rubrica='',
              resultado_criterio='', usuario_revisor_id=None):
        """Registra la evaluación de inmediato y notifica al estudiante. Si el
        ejecutor tiene rol Facultad (registrando en nombre de un jurado/tutor),
        además abre una Aprobacion pendiente para que un Decano la revise
        (supervisión posterior, no bloqueante) — requiere `usuario_revisor_id`."""
        EvaluacionProcesoValidator.validar_creacion(
            evaluador_id, instancia_etapa_id, nota, peso, concepto, aprobado, resultado,
        )

        es_facultad = ejecutor_es_facultad(ejecutor)
        if es_facultad and not usuario_revisor_id:
            raise ValidationError(
                {"usuario_revisor_id": "Debe indicar el Decano que revisará esta evaluación."}
            )

        evaluacion = EvaluacionProceso.objects.create(
            evaluador_id=evaluador_id,
            instancia_etapa_id=instancia_etapa_id,
            concepto=concepto,
            aprobado=aprobado,
            nota=nota,
            tipo_evaluador=tipo_evaluador,
            tipo_evaluacion=tipo_evaluacion,
            peso=peso,
            resultado=resultado,
            es_tercer_evaluador=es_tercer_evaluador,
            observaciones=observaciones,
            rubrica_evaluacion=rubrica_evaluacion,
            criterio_rubrica=criterio_rubrica,
            resultado_criterio=resultado_criterio,
        )
        # NOTA: el modelo cachea internamente en su save() el tope de nota 3.5
        # cuando hay una SegundaInstancia activa para el proceso de la
        # instancia_etapa; ese ajuste ya ocurrió antes de llegar aquí, así
        # que 'evaluacion.nota' puede diferir del 'nota' recibido como argumento.
        estado_resultado = "APROBADO" if aprobado else "NO APROBADO"
        HistorialService.registrar(
            ejecutor,
            f"Se registró la evaluación de '{evaluacion.evaluador}' sobre la etapa "
            f"'{evaluacion.instancia_etapa.etapa.nombre}': {estado_resultado} "
            f"(nota={evaluacion.nota}, id={evaluacion.pk}).",
            objeto=evaluacion,
        )

        proceso = evaluacion.instancia_etapa.proceso
        notificar(
            usuario_id_estudiante_de_proceso(proceso),
            f"Se registró un concepto de evaluación sobre la etapa "
            f"'{evaluacion.instancia_etapa.etapa.nombre}' de tu proceso '{proceso.titulo}': "
            f"{estado_resultado} (nota={evaluacion.nota}).",
            tipo='info',
        )

        if es_facultad:
            tipo_documento = TipoDocumentoSelector.obtener_por_nombre(
                TIPO_DOCUMENTO_APROBACION_EVALUACION_PROCESO
            )
            aprobacion = AprobacionService.crear(
                usuario_revisor_id=usuario_revisor_id,
                tipo_documento_id=tipo_documento.pk,
                id_documento=evaluacion.pk,
                ejecutor=ejecutor,
                observacion=(
                    f"Evaluación de '{evaluacion.evaluador}' sobre la etapa "
                    f"'{evaluacion.instancia_etapa.etapa.nombre}' del proceso '{proceso.titulo}', "
                    f"registrada por Facultad: {estado_resultado} (nota={evaluacion.nota})."
                ),
            )
            notificar(
                usuario_revisor_id,
                f"Facultad registró una evaluación sobre '{proceso.titulo}'. Pendiente de tu "
                f"revisión (aprobacion id={aprobacion.pk}).",
                tipo='info',
            )

        return evaluacion