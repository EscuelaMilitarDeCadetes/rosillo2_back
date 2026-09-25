"""
Service de GradoEstudios.

Interfaz estándar definitiva: listar(), obtener(id), crear(...),
actualizar(id, ...), eliminar(id). @transaction.atomic uniforme en todos
los métodos de escritura. El Service crea/actualiza/elimina sobre el
Model directamente (no se introduce capa Repository).
"""
from django.db import transaction

from apps.common.services.historial_service import HistorialService
from apps.institucional.models import GradoEstudios
from apps.institucional.selectors.grado_estudios_selector import GradoEstudiosSelector
from apps.institucional.validators.grado_estudios_validator import GradoEstudiosValidator


class GradoEstudiosService:

    @staticmethod
    def listar():
        return GradoEstudiosSelector.listar()

    @staticmethod
    def obtener(grado_id):
        return GradoEstudiosSelector.obtener(grado_id)

    @staticmethod
    @transaction.atomic
    def crear(sigla_grado, descripcion, ejecutor):
        GradoEstudiosValidator.validar_creacion(sigla_grado, descripcion)
        HistorialService.registrar(
            ejecutor,
            f"Se registró la grado de estudios que lleva por nombre '{sigla_grado} ' "
            f"y cuya descripcion es '{descripcion}'",
        )
        return GradoEstudios.objects.create(
            sigla_grado=sigla_grado.strip().upper(),
            descripcion=descripcion.strip(),
        )

    @staticmethod
    @transaction.atomic
    def actualizar(grado_id, sigla_grado, descripcion, ejecutor):
        grado = GradoEstudiosSelector.obtener(grado_id)
        GradoEstudiosValidator.validar_actualizacion(grado_id, sigla_grado, descripcion)
        grado.sigla_grado = sigla_grado.strip().upper()
        grado.descripcion = descripcion.strip()
        grado.save(update_fields=["sigla_grado", "descripcion"])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la grado de estudios que lleva por nombre '{sigla_grado} ' "
            f"y cuya descripcion es '{descripcion}'",
        )
        return grado