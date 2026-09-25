from django.db import transaction
from django.utils import timezone
from apps.investigacion_formativa.models import CertificacionExterna
from apps.investigacion_formativa.selectors.certificacion_externa_selector import (
    CertificacionExternaSelector,
)
from apps.investigacion_formativa.validators.certificacion_externa_validator import (
    CertificacionExternaValidator,
)
from apps.common.services.historial_service import HistorialService
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)
from apps.investigacion_formativa.services._soporte import (
    notificar,
    usuario_id_estudiante_de_proceso,
    validar_ejecutor_autor_o_gestor_por_proceso,
)

HORAS_MINIMAS_CUMPLIMIENTO = 120


class CertificacionExternaService:

    @staticmethod
    def listar():
        return CertificacionExternaSelector.listar()

    @staticmethod
    def obtener(certificacion_id):
        return CertificacionExternaSelector.obtener(certificacion_id)

    @staticmethod
    def listar_por_proceso(proceso_id):
        return CertificacionExternaSelector.listar_por_proceso(proceso_id)

    @staticmethod
    def listar_pendientes_validacion(proceso_id=None):
        return CertificacionExternaSelector.listar_pendientes_validacion(proceso_id=proceso_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_id, tipo, nombre_programa, institucion, horas_certificadas,
            fecha_inicio, fecha_fin, ejecutor, certificado_asistencia_id=None):
        CertificacionExternaValidator.validar_creacion(
            proceso_id, tipo, nombre_programa, institucion, horas_certificadas,
            fecha_inicio, fecha_fin, certificado_asistencia_id,
        )
        proceso = ProcesoFormativoSelector.obtener(proceso_id)
        # El estudiante solo puede registrar certificaciones de SU propio
        # proceso; Facultad/Decano pueden hacerlo en su nombre.
        validar_ejecutor_autor_o_gestor_por_proceso(
            proceso, ejecutor, "esta certificación externa"
        )
        certificacion = CertificacionExterna.objects.create(
            proceso_id=proceso_id,
            certificado_asistencia_id=certificado_asistencia_id,
            tipo=tipo,
            nombre_programa=nombre_programa,
            institucion=institucion,
            horas_certificadas=horas_certificadas,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            horas_validadas=0,
            cumple_horas=False,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró la certificación externa '{certificacion.nombre_programa}' "
            f"({certificacion.institucion}) del proceso '{certificacion.proceso.titulo}' "
            f"(id={certificacion.pk}).",
            objeto=certificacion,
        )
        return certificacion


    @staticmethod
    @transaction.atomic
    def actualizar(certificacion_id, tipo, nombre_programa, institucion, horas_certificadas,
                    fecha_inicio, fecha_fin, ejecutor):
        certificacion = CertificacionExternaSelector.obtener(certificacion_id)
        validar_ejecutor_autor_o_gestor_por_proceso(
            certificacion.proceso, ejecutor, "esta certificación externa"
        )
        CertificacionExternaValidator.validar_actualizacion(
            certificacion, tipo, nombre_programa, institucion, horas_certificadas,
            fecha_inicio, fecha_fin,
        )
        certificacion.tipo = tipo
        certificacion.nombre_programa = nombre_programa
        certificacion.institucion = institucion
        certificacion.horas_certificadas = horas_certificadas
        certificacion.fecha_inicio = fecha_inicio
        certificacion.fecha_fin = fecha_fin
        certificacion.save(update_fields=[
            'tipo', 'nombre_programa', 'institucion', 'horas_certificadas',
            'fecha_inicio', 'fecha_fin',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la certificación externa '{certificacion.nombre_programa}' (id={certificacion.pk}).",
            objeto=certificacion,
        )
        return certificacion

    @staticmethod
    @transaction.atomic
    def adjuntar_certificado_asistencia(certificacion_id, certificado_asistencia_id, ejecutor):
        certificacion = CertificacionExternaSelector.obtener(certificacion_id)
        validar_ejecutor_autor_o_gestor_por_proceso(
            certificacion.proceso, ejecutor, "esta certificación externa"
        )
        CertificacionExternaValidator.validar_adjuncion_certificado_asistencia(
            certificacion, certificado_asistencia_id
        )
        certificacion.certificado_asistencia_id = certificado_asistencia_id
        certificacion.save(update_fields=['certificado_asistencia'])
        HistorialService.registrar(
            ejecutor,
            f"Se adjuntó el certificado de asistencia a la certificación externa "
            f"'{certificacion.nombre_programa}' (id={certificacion.pk}).",
            objeto=certificacion,
        )
        return certificacion

    @staticmethod
    @transaction.atomic
    def validar_horas(certificacion_id, horas_validadas, validado_por_id, ejecutor):
        # Sin cambios: acción exclusivamente administrativa
        # (ROLES_VALIDACION_CERTIFICACION_EXTERNA = Facultad/Decano), no requiere
        # chequeo de autoría.
        certificacion = CertificacionExternaSelector.obtener(certificacion_id)
        CertificacionExternaValidator.validar_validacion_horas(
            certificacion, horas_validadas, validado_por_id
        )
        certificacion.horas_validadas = horas_validadas
        certificacion.cumple_horas = horas_validadas >= HORAS_MINIMAS_CUMPLIMIENTO
        certificacion.validado_por_id = validado_por_id
        certificacion.fecha_validacion = timezone.now()
        certificacion.save(update_fields=[
            'horas_validadas', 'cumple_horas', 'validado_por', 'fecha_validacion',
        ])
        resultado = "cumple" if certificacion.cumple_horas else "no cumple"
        HistorialService.registrar(
            ejecutor,
            f"Se validaron {horas_validadas} h de la certificación "
            f"'{certificacion.nombre_programa}' ({resultado} el mínimo de "
            f"{HORAS_MINIMAS_CUMPLIMIENTO} h, id={certificacion.pk}).",
            objeto=certificacion,
        )
        notificar(
            usuario_id_estudiante_de_proceso(certificacion.proceso),
            f"Se validaron {horas_validadas} h de tu certificación externa "
            f"'{certificacion.nombre_programa}' ({resultado} el mínimo requerido).",
            tipo='info' if certificacion.cumple_horas else 'alerta',
        )
        return certificacion

    @staticmethod
    @transaction.atomic
    def adjuntar_certificado_aprobacion(certificacion_id, certificado_aprobacion_id, ejecutor):
        # Sin cambios: acción administrativa (carga el acta que emite Facultad).
        certificacion = CertificacionExternaSelector.obtener(certificacion_id)
        CertificacionExternaValidator.validar_adjuncion_certificado(
            certificacion, certificado_aprobacion_id
        )
        certificacion.certificado_aprobacion_id = certificado_aprobacion_id
        certificacion.save(update_fields=['certificado_aprobacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se adjuntó el certificado de aprobación a la certificación externa "
            f"'{certificacion.nombre_programa}' (id={certificacion.pk}).",
            objeto=certificacion,
        )
        return certificacion

    @staticmethod
    @transaction.atomic
    def eliminar(certificacion_id, ejecutor):
        certificacion = CertificacionExternaSelector.obtener(certificacion_id)
        validar_ejecutor_autor_o_gestor_por_proceso(
            certificacion.proceso, ejecutor, "esta certificación externa"
        )
        CertificacionExternaValidator.validar_eliminacion(certificacion)
        certificacion.activo = False
        certificacion.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó la certificación externa '{certificacion.nombre_programa}' "
            f"del proceso '{certificacion.proceso.titulo}' (id={certificacion.pk}).",
            objeto=certificacion,
        )
        return certificacion