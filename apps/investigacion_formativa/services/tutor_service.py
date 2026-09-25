# apps/investigacion_formativa/services/tutor_service.py
from django.db import transaction

from apps.investigacion_formativa.models import Tutor
from apps.investigacion_formativa.selectors.tutor_selector import TutorSelector
from apps.investigacion_formativa.validators.tutor_validator import TutorValidator
from apps.common.services.historial_service import HistorialService


class TutorService:

    @staticmethod
    def listar():
        return TutorSelector.listar()

    @staticmethod
    def obtener(tutor_id):
        return TutorSelector.obtener(tutor_id)

    @staticmethod
    def listar_activos_por_facultad(facultad_id):
        return TutorSelector.listar_activos_por_facultad(facultad_id)

    @staticmethod
    @transaction.atomic
    def crear(persona_id, facultad_id, ejecutor):
        TutorValidator.validar_creacion(persona_id, facultad_id)
        tutor = Tutor.objects.create(
            persona_id=persona_id,
            facultad_id=facultad_id,
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró a '{tutor.persona}' como tutor de la facultad "
            f"'{tutor.facultad.nombre_facultad}' (id={tutor.pk}).",
            objeto=tutor,
        )
        return tutor

    @staticmethod
    @transaction.atomic
    def actualizar(tutor_id, facultad_id, ejecutor):
        tutor = TutorSelector.obtener(tutor_id)
        TutorValidator.validar_actualizacion(tutor, facultad_id)
        tutor.facultad_id = facultad_id
        tutor.save(update_fields=['facultad'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la facultad del tutor '{tutor.persona}' (id={tutor.pk}) a "
            f"'{tutor.facultad.nombre_facultad}'.",
            objeto=tutor,
        )
        return tutor

    @staticmethod
    @transaction.atomic
    def activar(tutor_id, ejecutor):
        tutor = TutorSelector.obtener(tutor_id)
        TutorValidator.validar_activacion(tutor)
        tutor.estado = True
        tutor.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se activó al tutor '{tutor.persona}' (id={tutor.pk}).",
            objeto=tutor,
        )
        return tutor

    @staticmethod
    @transaction.atomic
    def desactivar(tutor_id, ejecutor):
        tutor = TutorSelector.obtener(tutor_id)
        TutorValidator.validar_desactivacion(tutor)
        tutor.estado = False
        tutor.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó al tutor '{tutor.persona}' (id={tutor.pk}).",
            objeto=tutor,
        )
        return tutor