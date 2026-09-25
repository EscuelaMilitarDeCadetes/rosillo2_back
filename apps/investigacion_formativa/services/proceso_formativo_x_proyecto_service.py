from django.db import transaction

from apps.investigacion_formativa.models import ProcesoFormativoXProyecto
from apps.investigacion_formativa.selectors.proceso_formativo_x_proyecto_selector import (
    ProcesoFormativoXProyectoSelector,
)
from apps.investigacion_formativa.validators.proceso_formativo_x_proyecto_validator import (
    ProcesoFormativoXProyectoValidator,
)
from apps.common.services.historial_service import HistorialService


class ProcesoFormativoXProyectoService:

    @staticmethod
    def listar():
        return ProcesoFormativoXProyectoSelector.listar()

    @staticmethod
    def obtener(vinculo_id):
        return ProcesoFormativoXProyectoSelector.obtener(vinculo_id)

    @staticmethod
    def listar_por_proceso_formativo(proceso_formativo_id):
        return ProcesoFormativoXProyectoSelector.listar_por_proceso_formativo(proceso_formativo_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_formativo_id, proyecto_formal_id, ejecutor):
        ProcesoFormativoXProyectoValidator.validar_creacion(proceso_formativo_id, proyecto_formal_id)
        vinculo = ProcesoFormativoXProyecto.objects.create(
            proceso_formativo_id=proceso_formativo_id,
            proyecto_formal_id=proyecto_formal_id,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se vinculó el proceso formativo '{vinculo.proceso_formativo.titulo}' con el "
            f"proyecto formal '{vinculo.proyecto_formal.titulo}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def actualizar(vinculo_id, proceso_formativo_id, proyecto_formal_id, ejecutor):
        vinculo = ProcesoFormativoXProyectoSelector.obtener(vinculo_id)
        ProcesoFormativoXProyectoValidator.validar_actualizacion(
            vinculo_id, proceso_formativo_id, proyecto_formal_id
        )
        vinculo.proceso_formativo_id = proceso_formativo_id
        vinculo.proyecto_formal_id = proyecto_formal_id
        vinculo.save(update_fields=['proceso_formativo', 'proyecto_formal'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la vinculación proceso-proyecto (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def eliminar(vinculo_id, ejecutor):
        vinculo = ProcesoFormativoXProyectoSelector.obtener(vinculo_id)
        ProcesoFormativoXProyectoValidator.validar_eliminacion(vinculo)
        proceso_titulo = vinculo.proceso_formativo.titulo
        proyecto_titulo = vinculo.proyecto_formal.titulo
        vinculo.activo = False
        vinculo.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) la vinculación entre el proceso '{proceso_titulo}' "
            f"y el proyecto '{proyecto_titulo}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo