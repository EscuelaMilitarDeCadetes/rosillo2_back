"""
Service de GrupoInvestigacion.

Interfaz estándar definitiva + método de negocio específico:
    listar(), obtener(id), crear(...), actualizar(id, ...), eliminar(id),
    listar_grupos_usuario(usuario_id)

Nota de nomenclatura: aunque devuelve un único objeto (o None), se adopta
el nombre 'listar_grupos_usuario' tal como lo fija el punto 14 del
consenso final, para mantener el mismo prefijo verbal que el resto de
consultas relacionadas con catálogos institucionales.
"""
from django.db import transaction

from apps.common.services.historial_service import HistorialService
from apps.institucional.models import GrupoInvestigacion
from apps.institucional.selectors.grupo_investigacion_selector import GrupoInvestigacionSelector
from apps.institucional.validators.grupo_investigacion_validator import GrupoInvestigacionValidator


class GrupoInvestigacionService:

    @staticmethod
    def listar():
        return GrupoInvestigacionSelector.listar()

    @staticmethod
    def obtener(grupo_id):
        return GrupoInvestigacionSelector.obtener(grupo_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre_grupo, sigla_grupo, clasificacion_grupo, ejecutor):
        GrupoInvestigacionValidator.validar_creacion(nombre_grupo, sigla_grupo, clasificacion_grupo)
        HistorialService.registrar(
            ejecutor,
            f"Se registró el grupo de investigación llamado '{nombre_grupo}' "
            f" cuyas siglas son '{sigla_grupo}' y en este momento ostenta una clasificacion '{clasificacion_grupo}'",
        )
        return GrupoInvestigacion.objects.create(
            nombre_grupo=nombre_grupo.strip(),
            sigla_grupo=sigla_grupo.strip().upper(),
            clasificacion_grupo=clasificacion_grupo.strip().upper(),
        )

    @staticmethod
    @transaction.atomic
    def actualizar(grupo_id, nombre_grupo, sigla_grupo, clasificacion_grupo, ejecutor):
        grupo = GrupoInvestigacionSelector.obtener(grupo_id)
        GrupoInvestigacionValidator.validar_actualizacion(grupo_id, nombre_grupo, sigla_grupo, clasificacion_grupo)
        grupo.nombre_grupo = nombre_grupo.strip()
        grupo.sigla_grupo = sigla_grupo.strip().upper()
        grupo.clasificacion_grupo = clasificacion_grupo.strip().upper()
        grupo.save(update_fields=["nombre_grupo", "sigla_grupo", "clasificacion_grupo"])
        HistorialService.registrar(
            ejecutor,
            f"Se registró el grupo de investigación llamado '{nombre_grupo}' "
            f" cuyas siglas son '{sigla_grupo}' y en este momento ostenta una clasificacion '{clasificacion_grupo}'",
        )
        return grupo

    @staticmethod
    def listar_grupos_usuario(usuario_id):
        """
        Equivalente a GrupoInvestigacionServicio.listarGruposXUsuario(id),
        sin el hack id!=15.
        """
        return GrupoInvestigacionSelector.obtener_grupo_usuario(usuario_id)