from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.proceso_formativo_x_proyecto_selector import (
    ProcesoFormativoXProyectoSelector,
)
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)


class ProcesoFormativoXProyectoValidator:

    @staticmethod
    def validar_creacion(proceso_formativo_id, proyecto_formal_id):
        ProcesoFormativoXProyectoValidator._validar_proceso_formativo(proceso_formativo_id)
        ProcesoFormativoXProyectoValidator._validar_proyecto_formal(proyecto_formal_id)
        ProcesoFormativoXProyectoValidator._validar_unicidad(proceso_formativo_id, proyecto_formal_id)

    @staticmethod
    def validar_actualizacion(vinculo_id, proceso_formativo_id, proyecto_formal_id):
        ProcesoFormativoXProyectoValidator._validar_proceso_formativo(proceso_formativo_id)
        ProcesoFormativoXProyectoValidator._validar_proyecto_formal(proyecto_formal_id)
        ProcesoFormativoXProyectoValidator._validar_unicidad(
            proceso_formativo_id, proyecto_formal_id, excluir_id=vinculo_id
        )

    @staticmethod
    def validar_eliminacion(vinculo):
        if not vinculo.activo:
            raise ValidationError("Esta vinculación ya se encuentra desactivada.")

    @staticmethod
    def _validar_proceso_formativo(proceso_formativo_id):
        if not proceso_formativo_id:
            raise ValidationError({"proceso_formativo": "El proceso formativo es obligatorio."})
        if not ProcesoFormativoSelector.existe(proceso_formativo_id):
            raise ValidationError(
                {"proceso_formativo": f"No existe un ProcesoFormativo con id={proceso_formativo_id}."}
            )

    @staticmethod
    def _validar_proyecto_formal(proyecto_formal_id):
        if not proyecto_formal_id:
            raise ValidationError({"proyecto_formal": "El proyecto formal es obligatorio."})
        # Import diferido: investigacion_formal no es dependencia directa de investigacion_formativa
        from apps.investigacion_formal.models import Proyecto

        if not Proyecto.objects.filter(pk=proyecto_formal_id).exists():
            raise ValidationError({"proyecto_formal": f"No existe un Proyecto con id={proyecto_formal_id}."})

    @staticmethod
    def _validar_unicidad(proceso_formativo_id, proyecto_formal_id, excluir_id=None):
        if ProcesoFormativoXProyectoSelector.existe_combinacion(
            proceso_formativo_id, proyecto_formal_id, excluir_id=excluir_id
        ):
            raise ValidationError(
                "Este proceso formativo ya está vinculado a este proyecto formal."
            )