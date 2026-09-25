from django.db import transaction

from apps.investigacion_formativa.models import Estudiante
from apps.investigacion_formativa.selectors.estudiante_selector import EstudianteSelector
from apps.investigacion_formativa.validators.estudiante_validator import EstudianteValidator
from apps.common.services.historial_service import HistorialService


class EstudianteService:

    @staticmethod
    def listar():
        return EstudianteSelector.listar()

    @staticmethod
    def obtener(estudiante_id):
        return EstudianteSelector.obtener(estudiante_id)
    
    @staticmethod
    def listar_por_facultad(facultad_id, estado=None):
        return EstudianteSelector.listar_por_facultad(facultad_id, estado=estado)

    @staticmethod
    def listar_por_modalidad(modalidad_id, estado=None):
        return EstudianteSelector.listar_por_modalidad(modalidad_id, estado=estado)
    
    @staticmethod
    def listar_por_modalidad_facultad(modalidad_facultad_id, estado=None):
        return EstudianteSelector.listar_por_modalidad_facultad(modalidad_facultad_id, estado=estado)

    @staticmethod
    @transaction.atomic
    def crear(persona_id, modalidad_facultad_id, correo_personal, nivel, ejecutor):
        EstudianteValidator.validar_creacion(
            persona_id, correo_personal, nivel
        )
        estudiante = Estudiante.objects.create(
            persona_id=persona_id,
            modalidad_facultad_id=modalidad_facultad_id,
            correo_personal=correo_personal,
            nivel=nivel,
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró a '{estudiante.persona}' como estudiante de investigación "
            f"formativa (id={estudiante.pk}).",
            objeto=estudiante,
        )
        return estudiante

    @staticmethod
    @transaction.atomic
    def actualizar(estudiante_id, correo_personal, nivel, ejecutor):
        estudiante = EstudianteSelector.obtener(estudiante_id)
        EstudianteValidator.validar_actualizacion(correo_personal, nivel)
        estudiante.correo_personal = correo_personal
        estudiante.nivel = nivel
        estudiante.save(update_fields=['correo_personal', 'nivel'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizaron los datos del estudiante '{estudiante.persona}' (id={estudiante.pk}).",
            objeto=estudiante,
        )
        return estudiante

    @staticmethod
    @transaction.atomic
    def activar(estudiante_id, ejecutor):
        estudiante = EstudianteSelector.obtener(estudiante_id)
        EstudianteValidator.validar_activacion(estudiante)
        estudiante.estado = True
        estudiante.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se activó al estudiante '{estudiante.persona}' (id={estudiante.pk}).",
            objeto=estudiante,
        )
        return estudiante

    @staticmethod
    @transaction.atomic
    def eliminar(estudiante_id, ejecutor):
        estudiante = EstudianteSelector.obtener(estudiante_id)
        EstudianteValidator.validar_eliminacion(estudiante)
        estudiante.estado = False
        estudiante.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) al estudiante '{estudiante.persona}' (id={estudiante.pk}).",
            objeto=estudiante,
        )
        return estudiante