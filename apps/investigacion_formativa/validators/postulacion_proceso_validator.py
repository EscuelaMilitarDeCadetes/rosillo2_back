# apps/investigacion_formativa/validators/postulacion_proceso_validator.py

from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.postulacion_proceso_selector import (
    PostulacionProcesoSelector,
)
from apps.investigacion_formativa.selectors.estudiante_selector import EstudianteSelector
from apps.investigacion_formativa.selectors.modalidad_x_facultad_selector import (
    ModalidadXFacultadSelector,
)

ESTADOS_EDITABLES = {'BORRADOR'}
ESTADOS_RECHAZABLES = {'ENVIADA', 'EN_VALIDACION'}


class PostulacionProcesoValidator:

    @staticmethod
    def validar_creacion(estudiante_id, modalidad_id, promedio_actual):
        PostulacionProcesoValidator._validar_estudiante(estudiante_id)
        PostulacionProcesoValidator._validar_modalidad(modalidad_id)
        PostulacionProcesoValidator._validar_promedio_actual(promedio_actual)
        PostulacionProcesoValidator._validar_unicidad_postulacion(estudiante_id, modalidad_id)
        PostulacionProcesoValidator._validar_correspondencia_facultad(estudiante_id, modalidad_id)
        PostulacionProcesoValidator._validar_sin_proceso_vigente(estudiante_id)

    @staticmethod
    def validar_actualizacion(postulacion, promedio_actual):
        PostulacionProcesoValidator._validar_editable(postulacion)
        PostulacionProcesoValidator._validar_promedio_actual(promedio_actual)

    @staticmethod
    def validar_envio(postulacion):
        """BORRADOR -> ENVIADA."""
        if postulacion.estado != 'BORRADOR':
            raise ValidationError(
                f"No se puede enviar una postulación en estado '{postulacion.estado}'."
            )

    @staticmethod
    def validar_paso_a_validacion(postulacion):
        """ENVIADA -> EN_VALIDACION."""
        if postulacion.estado != 'ENVIADA':
            raise ValidationError(
                f"No se puede pasar a validación una postulación en estado '{postulacion.estado}'."
            )

    @staticmethod
    def validar_aprobacion(postulacion):
        """EN_VALIDACION -> APROBADA. Genera el ProcesoFormativo asociado."""
        if postulacion.estado != 'EN_VALIDACION':
            raise ValidationError(
                "Solo se puede aprobar una postulación que se encuentre en estado 'EN_VALIDACION'."
            )
        if postulacion.proceso_creado_id is not None:
            raise ValidationError("Esta postulación ya generó un proceso formativo.")

    @staticmethod
    def validar_rechazo(postulacion, observacion_coordinacion):
        if postulacion.estado not in ESTADOS_RECHAZABLES:
            raise ValidationError(
                f"No se puede rechazar una postulación en estado '{postulacion.estado}'."
            )
        if not observacion_coordinacion or not observacion_coordinacion.strip():
            raise ValidationError(
                {"observacion_coordinacion": "Debe indicar el motivo del rechazo de la postulación."}
            )

    @staticmethod
    def validar_eliminacion(postulacion):
        if postulacion.estado != 'BORRADOR':
            raise ValidationError("No se puede eliminar una postulación que ya fue enviada.")

    @staticmethod
    def _validar_estudiante(estudiante_id):
        if not estudiante_id:
            raise ValidationError({"estudiante": "El estudiante es obligatorio."})
        if not EstudianteSelector.existe(estudiante_id):
            raise ValidationError({"estudiante": f"No existe un Estudiante con id={estudiante_id}."})

    @staticmethod
    def _validar_modalidad(modalidad_id):
        if not modalidad_id:
            raise ValidationError({"modalidad": "La modalidad es obligatoria."})
        if not ModalidadXFacultadSelector.existe(modalidad_id):
            raise ValidationError({"modalidad": f"No existe una ModalidadXFacultad con id={modalidad_id}."})

    @staticmethod
    def _validar_correspondencia_facultad(estudiante_id, modalidad_id):
        """Un estudiante nunca puede postular a una modalidad de una facultad
        distinta a la suya (misma regla que RN-07 de PersonaXGrupo/FacultadXGrupo)."""
        estudiante = EstudianteSelector.obtener(estudiante_id)
        modalidad_facultad = ModalidadXFacultadSelector.obtener(modalidad_id)
        if estudiante.modalidad_facultad.facultad_id != modalidad_facultad.facultad_id:
            raise ValidationError(
                {"modalidad": "El estudiante no puede postular a una modalidad de una facultad distinta a la suya."}
            )

    @staticmethod
    def _validar_promedio_actual(promedio_actual):
        if promedio_actual is None:
            raise ValidationError({"promedio_actual": "El promedio académico actual es obligatorio."})
        try:
            valor = float(promedio_actual)
        except (TypeError, ValueError):
            raise ValidationError({"promedio_actual": "El promedio debe ser numérico."})
        if valor < 0 or valor > 5:
            raise ValidationError({"promedio_actual": "El promedio debe estar entre 0.0 y 5.0."})

    @staticmethod
    def _validar_editable(postulacion):
        if postulacion.estado not in ESTADOS_EDITABLES:
            raise ValidationError(
                f"No se puede editar una postulación en estado '{postulacion.estado}'."
            )

    @staticmethod
    def _validar_unicidad_postulacion(estudiante_id, modalidad_id):
        if PostulacionProcesoSelector.existe_postulacion(estudiante_id, modalidad_id):
            raise ValidationError(
                "Este estudiante ya tiene una postulación registrada para esta modalidad."
            )
    
    @staticmethod
    def _validar_sin_proceso_vigente(estudiante_id):
        """Un estudiante solo puede cursar una modalidad de grado a la vez.
        Si su última postulación aprobada generó un ProcesoFormativo que
        aún no ha sido calificado (aprobado is None) o que fue aprobado
        (aprobado=True), no puede postular a una modalidad nueva. Si ese
        proceso fue calificado como reprobado (aprobado=False), queda
        habilitado para postular de nuevo a cualquier modalidad de su
        facultad."""
        ultima = PostulacionProcesoSelector.obtener_ultima_aprobada(estudiante_id)
        if ultima is None or ultima.proceso_creado is None:
            return
        proceso = ultima.proceso_creado
        if proceso.aprobado is not False:
            estado_legible = "en curso" if proceso.aprobado is None else "aprobado"
            raise ValidationError(
                f"El estudiante ya tiene un proceso de grado {estado_legible} "
                f"('{proceso.titulo}'). Solo puede postular a una modalidad nueva "
                "si su proceso anterior fue calificado como reprobado."
            )