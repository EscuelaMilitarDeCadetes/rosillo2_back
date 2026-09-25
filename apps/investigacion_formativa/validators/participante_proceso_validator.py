from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.participante_proceso_selector import (
    ParticipanteProcesoSelector,
)
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)

ROLES_PARTICIPANTE_VALIDOS = {
    'ESTUDIANTE', 'TUTOR', 'JURADO', 'INVESTIGADOR_PRINCIPAL', 'COORDINADOR', 'OTRO',
}


class ParticipanteProcesoValidator:

    @staticmethod
    def validar_creacion(proceso_formativo_id, persona_id, rol_en_modalidad, fecha_finalizacion=None):
        ParticipanteProcesoValidator._validar_proceso_formativo(proceso_formativo_id)
        ParticipanteProcesoValidator._validar_persona(persona_id)
        ParticipanteProcesoValidator._validar_rol(rol_en_modalidad)
        ParticipanteProcesoValidator._validar_fecha_finalizacion(fecha_finalizacion)
        ParticipanteProcesoValidator._validar_unicidad_participante(proceso_formativo_id, persona_id)

    @staticmethod
    def validar_actualizacion(participante, rol_en_modalidad, fecha_finalizacion=None):
        ParticipanteProcesoValidator._validar_rol(rol_en_modalidad)
        ParticipanteProcesoValidator._validar_fecha_finalizacion(fecha_finalizacion)
        if fecha_finalizacion is not None and fecha_finalizacion < participante.fecha_asignacion:
            raise ValidationError(
                {"fecha_finalizacion": "La fecha de finalización no puede ser anterior a la fecha de asignación."}
            )

    @staticmethod
    def validar_finalizacion(participante):
        """Réplica del cierre de participación: no se puede finalizar dos veces."""
        if participante.fecha_finalizacion is not None:
            raise ValidationError("Este participante ya fue finalizado en el proceso.")
        if not participante.activo:
            raise ValidationError("No se puede finalizar un participante ya desactivado.")

    @staticmethod
    def validar_eliminacion(participante):
        if not participante.activo:
            raise ValidationError("Este participante ya se encuentra desactivado.")

    @staticmethod
    def _validar_proceso_formativo(proceso_formativo_id):
        if not proceso_formativo_id:
            raise ValidationError({"proceso_formativo": "El proceso formativo es obligatorio."})
        if not ProcesoFormativoSelector.existe(proceso_formativo_id):
            raise ValidationError(
                {"proceso_formativo": f"No existe un ProcesoFormativo con id={proceso_formativo_id}."}
            )

    @staticmethod
    def _validar_persona(persona_id):
        if not persona_id:
            raise ValidationError({"persona": "La persona es obligatoria."})
        # Import diferido: institucional no es dependencia directa de investigacion_formativa
        from apps.institucional.models import Persona

        if not Persona.objects.filter(pk=persona_id).exists():
            raise ValidationError({"persona": f"No existe una Persona con id={persona_id}."})

    @staticmethod
    def _validar_rol(rol_en_modalidad):
        if not rol_en_modalidad:
            raise ValidationError({"rol_en_modalidad": "El rol del participante es obligatorio."})
        if rol_en_modalidad not in ROLES_PARTICIPANTE_VALIDOS:
            raise ValidationError(
                {"rol_en_modalidad": (
                    f"'{rol_en_modalidad}' no es un rol válido. "
                    f"Use uno de: {sorted(ROLES_PARTICIPANTE_VALIDOS)}."
                )}
            )

    @staticmethod
    def _validar_fecha_finalizacion(fecha_finalizacion):
        # Campo opcional; no hay más restricción de formato porque DRF ya
        # tipa el campo como DateField a nivel de serializer.
        pass

    @staticmethod
    def _validar_unicidad_participante(proceso_formativo_id, persona_id, excluir_id=None):
        existente = ParticipanteProcesoSelector.obtener_por_proceso_y_persona(proceso_formativo_id, persona_id)
        if existente is not None and (excluir_id is None or existente.pk != excluir_id):
            raise ValidationError(
                "Esta persona ya está registrada como participante en este proceso formativo."
            )