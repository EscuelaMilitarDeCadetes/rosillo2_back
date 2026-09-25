from django.db import transaction

from apps.investigacion_formal.models import RolInvestigador
from apps.investigacion_formal.selectors.rol_investigador_selector import RolInvestigadorSelector
from apps.investigacion_formal.validators.rol_investigador_validator import RolInvestigadorValidator
from apps.common.services.historial_service import HistorialService


class RolInvestigadorService:

    @staticmethod
    def listar():
        return RolInvestigadorSelector.listar()

    @staticmethod
    def obtener(rol_investigador_id):
        return RolInvestigadorSelector.obtener(rol_investigador_id)

    @staticmethod
    @transaction.atomic
    def crear(nombre_rol_investigador, descripcion, ejecutor):
        RolInvestigadorValidator.validar_creacion(nombre_rol_investigador, descripcion)
        rol = RolInvestigador.objects.create(
            nombre_rol_investigador=nombre_rol_investigador.strip(),
            descripcion=descripcion.strip(),
        )
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se creó el rol de investigador "
            f"'{rol.nombre_rol_investigador}' (id={rol.pk}).",
            objeto=rol,
        )
        return rol

    @staticmethod
    @transaction.atomic
    def actualizar(rol_investigador_id, nombre_rol_investigador, descripcion, ejecutor):
        rol = RolInvestigadorSelector.obtener(rol_investigador_id)
        RolInvestigadorValidator.validar_actualizacion(
            rol_investigador_id, nombre_rol_investigador, descripcion
        )
        rol.nombre_rol_investigador = nombre_rol_investigador.strip()
        rol.descripcion = descripcion.strip()
        rol.save(update_fields=['nombre_rol_investigador', 'descripcion'])
        HistorialService.registrar(
            ejecutor,
            f"[SOPORTE] Se actualizó el rol de investigador "
            f"'{rol.nombre_rol_investigador}' (id={rol.pk}).",
            objeto=rol,
        )
        return rol