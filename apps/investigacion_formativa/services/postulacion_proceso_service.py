from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.investigacion_formativa.models import PostulacionProceso
from apps.common.services.historial_service import HistorialService
from apps.common.services.aprobacion_service import AprobacionService
from apps.common.selectors.aprobacion_selector import AprobacionSelector
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector
from apps.investigacion_formativa.selectors.estudiante_selector import EstudianteSelector
from apps.investigacion_formativa.selectors.postulacion_proceso_selector import (
    PostulacionProcesoSelector,
)
from apps.investigacion_formativa.validators.postulacion_proceso_validator import (
    PostulacionProcesoValidator,
)
from apps.investigacion_formativa.services.proceso_formativo_service import (
    ProcesoFormativoService,
)
from apps.investigacion_formativa.services._soporte import (
    notificar,
    usuario_id_de_persona,
    validar_ejecutor_autor_o_gestor,
)

TIPO_DOCUMENTO_APROBACION_POSTULACION = 'APROBACION_POSTULACION'


class PostulacionProcesoService:

    @staticmethod
    def listar():
        return PostulacionProcesoSelector.listar()

    @staticmethod
    def obtener(postulacion_id):
        return PostulacionProcesoSelector.obtener(postulacion_id)

    @staticmethod
    def listar_por_estudiante(estudiante_id):
        return PostulacionProcesoSelector.listar_por_estudiante(estudiante_id)

    @staticmethod
    def listar_pendientes_por_facultad(facultad_id):
        return PostulacionProcesoSelector.listar_pendientes_por_facultad(facultad_id)

    @staticmethod
    @transaction.atomic
    def crear(estudiante_id, modalidad_id, promedio_actual, ejecutor):
        PostulacionProcesoValidator.validar_creacion(estudiante_id, modalidad_id, promedio_actual)
        estudiante = EstudianteSelector.obtener(estudiante_id)
        # El estudiante solo puede postularse a sí mismo; Facultad/Decano
        # pueden crear la postulación en su nombre.
        validar_ejecutor_autor_o_gestor(
            estudiante.persona_id, ejecutor, "esta postulación"
        )
        postulacion = PostulacionProceso.objects.create(
            estudiante_id=estudiante_id,
            modalidad_id=modalidad_id,
            promedio_actual=promedio_actual,
            estado='BORRADOR',
        )        
        HistorialService.registrar(
            ejecutor,
            f"Se creó la postulación de '{postulacion.estudiante}' a la modalidad "
            f"'{postulacion.modalidad}' (id={postulacion.pk}).",
            objeto=postulacion,
        )
        return postulacion

    @staticmethod
    @transaction.atomic
    def actualizar(postulacion_id, promedio_actual, ejecutor):
        postulacion = PostulacionProcesoSelector.obtener(postulacion_id)
        validar_ejecutor_autor_o_gestor(
            postulacion.estudiante.persona_id, ejecutor, "esta postulación"
        )
        PostulacionProcesoValidator.validar_actualizacion(postulacion, promedio_actual)
        postulacion.promedio_actual = promedio_actual
        postulacion.save(update_fields=['promedio_actual'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el promedio de la postulación (id={postulacion.pk}) a {promedio_actual}.",
            objeto=postulacion,
        )
        return postulacion

    @staticmethod
    @transaction.atomic
    def enviar(postulacion_id, ejecutor):
        postulacion = PostulacionProcesoSelector.obtener(postulacion_id)
        validar_ejecutor_autor_o_gestor(
            postulacion.estudiante.persona_id, ejecutor, "esta postulación"
        )
        PostulacionProcesoValidator.validar_envio(postulacion)
        postulacion.estado = 'ENVIADA'
        postulacion.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se envió la postulación (id={postulacion.pk}) de '{postulacion.estudiante}'.",
            objeto=postulacion,
        )
        notificar(
            usuario_id_de_persona(postulacion.estudiante.persona),
            f"Tu postulación a '{postulacion.modalidad.modalidad.nombre}' fue enviada "
            f"y quedó a la espera de validación.",
            tipo='info',
        )
        return postulacion

    @staticmethod
    @transaction.atomic
    def pasar_a_validacion(postulacion_id, ejecutor):
        # Sin cambios: paso administrativo (Facultad/Decano/Soporte).
        postulacion = PostulacionProcesoSelector.obtener(postulacion_id)
        PostulacionProcesoValidator.validar_paso_a_validacion(postulacion)
        postulacion.estado = 'EN_VALIDACION'
        postulacion.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"La postulación (id={postulacion.pk}) pasó a validación de coordinación.",
            objeto=postulacion,
        )
        return postulacion

    @staticmethod
    @transaction.atomic
    def aprobar(postulacion_id, flujo_version_id, titulo, observacion, fecha_inicio, fecha_fin, ejecutor):
        """Aprueba la postulación y genera el ProcesoFormativo asociado.
        Si la modalidad aprobada difiere de la que el Estudiante tenía
        registrada (típicamente porque su proceso anterior fue reprobado y
        volvió a postular a otra modalidad), sincroniza
        Estudiante.modalidad_facultad con la nueva modalidad aprobada."""
        postulacion = PostulacionProcesoSelector.obtener(postulacion_id)
        PostulacionProcesoValidator.validar_aprobacion(postulacion)
        proceso = ProcesoFormativoService.crear(
            flujo_version_id=flujo_version_id,
            titulo=titulo,
            observacion=observacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ejecutor=ejecutor,
            idea_id=None,
            entidad_externa_id=None,
        )
        postulacion.proceso_creado = proceso
        postulacion.estado = 'APROBADA'
        postulacion.fecha_decision = timezone.now()
        postulacion.save(update_fields=['proceso_creado', 'estado', 'fecha_decision'])

        estudiante = postulacion.estudiante
        if estudiante.modalidad_facultad_id != postulacion.modalidad_id:
            modalidad_anterior = estudiante.modalidad_facultad
            estudiante.modalidad_facultad_id = postulacion.modalidad_id
            estudiante.save(update_fields=['modalidad_facultad'])
            HistorialService.registrar(
                ejecutor,
                f"El estudiante '{estudiante.persona}' cambió de modalidad "
                f"('{modalidad_anterior}' → '{postulacion.modalidad}') tras la "
                f"aprobación de la postulación (id={postulacion.pk}).",
                objeto=estudiante,
            )

        HistorialService.registrar(
            ejecutor,
            f"Se aprobó la postulación (id={postulacion.pk}) de '{postulacion.estudiante}' "
            f"y se generó el proceso formativo '{proceso.titulo}' (id={proceso.pk}).",
            objeto=postulacion,
        )
        notificar(
            usuario_id_de_persona(postulacion.estudiante.persona),
            f"¡Felicitaciones! Tu postulación a '{postulacion.modalidad.modalidad.nombre}' "
            f"fue aprobada. Se creó tu proceso de grado '{proceso.titulo}'.",
            tipo='exito',
        )
        return postulacion

    @staticmethod
    @transaction.atomic
    def rechazar(postulacion_id, observacion_coordinacion, ejecutor):
        # Sin cambios: acción administrativa.
        postulacion = PostulacionProcesoSelector.obtener(postulacion_id)
        PostulacionProcesoValidator.validar_rechazo(postulacion, observacion_coordinacion)
        postulacion.estado = 'RECHAZADA'
        postulacion.fecha_decision = timezone.now()
        postulacion.observacion_coordinacion = observacion_coordinacion
        postulacion.save(update_fields=['estado', 'fecha_decision', 'observacion_coordinacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se rechazó la postulación (id={postulacion.pk}) de '{postulacion.estudiante}': "
            f"{observacion_coordinacion}",
            objeto=postulacion,
        )
        notificar(
            usuario_id_de_persona(postulacion.estudiante.persona),
            f"Tu postulación a '{postulacion.modalidad.modalidad.nombre}' fue rechazada. "
            f"Motivo: {observacion_coordinacion}",
            tipo='alerta',
        )
        return postulacion

    @staticmethod
    @transaction.atomic
    def solicitar_decision_decano(postulacion_id, usuario_revisor_id, ejecutor, observacion=None):
        # Sin cambios: acción administrativa (Facultad -> Decano).
        postulacion = PostulacionProcesoSelector.obtener(postulacion_id)
        PostulacionProcesoValidator.validar_aprobacion(postulacion)
        if not usuario_revisor_id:
            raise ValidationError(
                {"usuario_revisor_id": "Debe indicar el Decano que revisará la postulación."}
            )
        tipo_documento = TipoDocumentoSelector.obtener_por_nombre(TIPO_DOCUMENTO_APROBACION_POSTULACION)
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=usuario_revisor_id,
            tipo_documento_id=tipo_documento.pk,
            id_documento=postulacion.pk,
            ejecutor=ejecutor,
            observacion=observacion,
        )
        HistorialService.registrar(
            ejecutor,
            f"La postulación (id={postulacion.pk}) de '{postulacion.estudiante}' quedó "
            f"pendiente de aprobación del Decano (aprobacion id={aprobacion.pk}).",
            objeto=postulacion,
        )
        notificar(
            usuario_revisor_id,
            f"Tienes una postulación pendiente de tu aprobación: "
            f"'{postulacion.estudiante}' a '{postulacion.modalidad.modalidad.nombre}'.",
            tipo='info',
        )
        return aprobacion

    @staticmethod
    @transaction.atomic
    def confirmar_aprobacion_decano(aprobacion_id, flujo_version_id, titulo, observacion,
                                     fecha_inicio, fecha_fin, ejecutor, observacion_decano=None):
        aprobacion = AprobacionSelector.obtener(aprobacion_id)
        if aprobacion.tipo_documento.nombre_documento != TIPO_DOCUMENTO_APROBACION_POSTULACION:
            raise ValidationError("La Aprobacion indicada no corresponde a una postulación.")
        AprobacionService.aprobar(aprobacion_id, ejecutor, observacion_decano)
        return PostulacionProcesoService.aprobar(
            postulacion_id=aprobacion.id_documento,
            flujo_version_id=flujo_version_id,
            titulo=titulo,
            observacion=observacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ejecutor=ejecutor,
        )

    @staticmethod
    @transaction.atomic
    def denegar_por_decano(aprobacion_id, ejecutor, observacion):
        aprobacion = AprobacionSelector.obtener(aprobacion_id)
        if aprobacion.tipo_documento.nombre_documento != TIPO_DOCUMENTO_APROBACION_POSTULACION:
            raise ValidationError("La Aprobacion indicada no corresponde a una postulación.")
        AprobacionService.rechazar(aprobacion_id, ejecutor, observacion)
        return PostulacionProcesoService.rechazar(
            postulacion_id=aprobacion.id_documento,
            observacion_coordinacion=observacion,
            ejecutor=ejecutor,
        )

    @staticmethod
    @transaction.atomic
    def eliminar(postulacion_id, ejecutor):
        postulacion = PostulacionProcesoSelector.obtener(postulacion_id)
        validar_ejecutor_autor_o_gestor(
            postulacion.estudiante.persona_id, ejecutor, "esta postulación"
        )
        PostulacionProcesoValidator.validar_eliminacion(postulacion)
        postulacion.estado = 'ELIMINADA'
        postulacion.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó la postulación de '{postulacion.estudiante}' a "
            f"'{postulacion.modalidad.modalidad.nombre}' (id={postulacion.pk}).",
            objeto=postulacion,
        )
        return postulacion