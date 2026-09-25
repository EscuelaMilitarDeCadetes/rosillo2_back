# apps/investigacion_formativa/validators/certificacion_externa_validator.py
from rest_framework.exceptions import ValidationError

TIPOS_VALIDOS = ('MINOR', 'DIPLOMADO', 'CATEDRA_INTERNACIONAL', 'OTRO')


class CertificacionExternaValidator:

    @staticmethod
    def validar_creacion(proceso_id, tipo, nombre_programa, institucion, horas_certificadas,
                          fecha_inicio, fecha_fin, certificado_asistencia_id=None):
        CertificacionExternaValidator._validar_proceso(proceso_id)
        CertificacionExternaValidator._validar_tipo(tipo)
        CertificacionExternaValidator._validar_nombre_programa(nombre_programa)
        CertificacionExternaValidator._validar_institucion(institucion)
        CertificacionExternaValidator._validar_horas_certificadas(horas_certificadas)
        CertificacionExternaValidator._validar_fechas(fecha_inicio, fecha_fin)
        if certificado_asistencia_id is not None:
            CertificacionExternaValidator.validar_adjuncion_certificado_asistencia(
                certificacion=None, certificado_asistencia_id=certificado_asistencia_id
            )
    @staticmethod
    def validar_actualizacion(certificacion, tipo, nombre_programa, institucion,
                               horas_certificadas, fecha_inicio, fecha_fin):
        if certificacion.fecha_validacion is not None:
            raise ValidationError(
                "No se puede modificar una certificación externa que ya fue validada."
            )
        CertificacionExternaValidator._validar_tipo(tipo)
        CertificacionExternaValidator._validar_nombre_programa(nombre_programa)
        CertificacionExternaValidator._validar_institucion(institucion)
        CertificacionExternaValidator._validar_horas_certificadas(horas_certificadas)
        CertificacionExternaValidator._validar_fechas(fecha_inicio, fecha_fin)

    @staticmethod
    def validar_adjuncion_certificado(certificacion, certificado_aprobacion_id):
        """Paso previo a la validación por parte de facultades."""
        if certificacion.fecha_validacion is not None:
            raise ValidationError(
                "Esta certificación ya fue validada; no se puede reemplazar el certificado de aprobación."
            )
        if certificado_aprobacion_id is None:
            raise ValidationError(
                {"certificado_aprobacion_id": "Debe indicar el documento del certificado de aprobación."}
            )

    @staticmethod
    def validar_validacion_horas(certificacion, horas_validadas, validado_por_id):
        """Ejecutado por el rol facultades al validar horas y decidir cumple_horas."""
        if certificacion.fecha_validacion is not None:
            raise ValidationError("Esta certificación ya fue validada previamente.")
        if certificacion.certificado_aprobacion_id is None:
            raise ValidationError(
                "No se puede validar una certificación sin certificado de aprobación cargado."
            )
        if validado_por_id is None:
            raise ValidationError({"validado_por_id": "Debe indicar quién valida las horas."})
        CertificacionExternaValidator._validar_horas_validadas(horas_validadas)

    @staticmethod
    def validar_eliminacion(certificacion):
        if not certificacion.activo:
            raise ValidationError("Esta certificación externa ya se encuentra eliminada.")
        if certificacion.fecha_validacion is not None:
            raise ValidationError("No se puede eliminar una certificación externa que ya fue validada.")

    @staticmethod
    def _validar_proceso(proceso_id):
        if not proceso_id:
            raise ValidationError({"proceso": "El proceso formativo es obligatorio."})

    @staticmethod
    def _validar_tipo(tipo):
        if tipo not in TIPOS_VALIDOS:
            raise ValidationError({"tipo": f"Tipo inválido. Debe ser uno de: {', '.join(TIPOS_VALIDOS)}."})

    @staticmethod
    def _validar_nombre_programa(nombre_programa):
        if not nombre_programa or not nombre_programa.strip():
            raise ValidationError({"nombre_programa": "El nombre del programa es obligatorio."})
        if len(nombre_programa) > 255:
            raise ValidationError({"nombre_programa": "El nombre del programa supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_institucion(institucion):
        if not institucion or not institucion.strip():
            raise ValidationError({"institucion": "La institución certificadora es obligatoria."})
        if len(institucion) > 200:
            raise ValidationError({"institucion": "La institución supera el máximo de 200 caracteres."})

    @staticmethod
    def _validar_horas_certificadas(horas_certificadas):
        if horas_certificadas is None:
            raise ValidationError({"horas_certificadas": "Las horas certificadas son obligatorias."})
        try:
            valor = float(horas_certificadas)
        except (TypeError, ValueError):
            raise ValidationError({"horas_certificadas": "Las horas certificadas deben ser numéricas."})
        if valor <= 0:
            raise ValidationError({"horas_certificadas": "Las horas certificadas deben ser mayores a 0."})

    @staticmethod
    def _validar_horas_validadas(horas_validadas):
        if horas_validadas is None:
            raise ValidationError({"horas_validadas": "Las horas validadas son obligatorias."})
        try:
            valor = float(horas_validadas)
        except (TypeError, ValueError):
            raise ValidationError({"horas_validadas": "Las horas validadas deben ser numéricas."})
        if valor < 0:
            raise ValidationError({"horas_validadas": "Las horas validadas no pueden ser negativas."})

    @staticmethod
    def _validar_fechas(fecha_inicio, fecha_fin):
        if not fecha_inicio or not fecha_fin:
            raise ValidationError("Las fechas de inicio y fin de la certificación son obligatorias.")
        if fecha_fin < fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."})
        
    @staticmethod
    def validar_adjuncion_certificado_asistencia(certificacion, certificado_asistencia_id):
        if certificacion.fecha_validacion is not None:
            raise ValidationError(
                "Esta certificación ya fue validada; no se puede reemplazar el certificado de asistencia."
            )
        if certificado_asistencia_id is None:
            raise ValidationError(
                {"certificado_asistencia_id": "Debe indicar el documento del certificado de asistencia."}
            )