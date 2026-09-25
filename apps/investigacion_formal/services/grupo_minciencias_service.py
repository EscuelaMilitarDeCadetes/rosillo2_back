from django.db import transaction

from apps.investigacion_formal.models import GrupoMinciencias
from apps.investigacion_formal.selectors.grupo_minciencias_selector import GrupoMincienciasSelector
from apps.investigacion_formal.validators.grupo_minciencias_validator import GrupoMincienciasValidator
from apps.common.services.historial_service import HistorialService


class GrupoMincienciasService:

    @staticmethod
    def listar():
        return GrupoMincienciasSelector.listar()

    @staticmethod
    def obtener(grupo_minciencias_id):
        return GrupoMincienciasSelector.obtener(grupo_minciencias_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre_grupo_minciencias, ejecutor):
        GrupoMincienciasValidator.validar_creacion(nombre_grupo_minciencias)
        grupo = GrupoMinciencias.objects.create(
            nombre_grupo_minciencias=nombre_grupo_minciencias.strip()
        )
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se creó el grupo Minciencias '{grupo.nombre_grupo_minciencias}' "
            f"(id={grupo.pk}).",
            objeto=grupo,
        )
        return grupo

    @staticmethod
    @transaction.atomic
    def actualizar(grupo_minciencias_id, nombre_grupo_minciencias, ejecutor):
        grupo = GrupoMincienciasSelector.obtener(grupo_minciencias_id)
        GrupoMincienciasValidator.validar_actualizacion(
            grupo_minciencias_id, nombre_grupo_minciencias
        )
        grupo.nombre_grupo_minciencias = nombre_grupo_minciencias.strip()
        grupo.save(update_fields=['nombre_grupo_minciencias'])
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se actualizó el grupo Minciencias a "
            f"'{grupo.nombre_grupo_minciencias}' (id={grupo.pk}).",
            objeto=grupo,
        )
        return grupo