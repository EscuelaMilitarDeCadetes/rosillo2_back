"""
Service de RolGrupo.

Interfaz estándar definitiva con @transaction.atomic uniforme.
"""
from django.db import transaction

from apps.common.services.historial_service import HistorialService
from apps.institucional.models import RolGrupo
from apps.institucional.selectors.rol_grupo_selector import RolGrupoSelector
from apps.institucional.validators.rol_grupo_validator import RolGrupoValidator


class RolGrupoService:

    @staticmethod
    def listar():
        return RolGrupoSelector.listar()

    @staticmethod
    def obtener(rol_grupo_id):
        return RolGrupoSelector.obtener(rol_grupo_id)

    @staticmethod
    @transaction.atomic
    def crear(cargo, ejecutor):
        RolGrupoValidator.validar_creacion(cargo)
        HistorialService.registrar(
            ejecutor,
            f"Se registró el rol del grupo '{cargo}' ",
        )
        return RolGrupo.objects.create(cargo=cargo.strip())

    @staticmethod
    @transaction.atomic
    def actualizar(rol_grupo_id, cargo, ejecutor):
        rol_grupo = RolGrupoSelector.obtener(rol_grupo_id)
        RolGrupoValidator.validar_actualizacion(rol_grupo_id, cargo)
        rol_grupo.cargo = cargo.strip()
        rol_grupo.save(update_fields=["cargo"])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el rol del grupo '{cargo}' ",
        )
        return rol_grupo