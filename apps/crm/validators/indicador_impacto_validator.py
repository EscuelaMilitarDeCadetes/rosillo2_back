from rest_framework.exceptions import ValidationError

from apps.crm.selectors.indicador_impacto_selector import IndicadorImpactoSelector


class IndicadorImpactoValidator:

    @staticmethod
    def validar_creacion(proyecto_id, kpi_nombre, valor_proyectado, valor_real=None):
        IndicadorImpactoValidator._validar_proyecto(proyecto_id)
        IndicadorImpactoValidator._validar_kpi_nombre(kpi_nombre)
        IndicadorImpactoValidator._validar_valor_proyectado(valor_proyectado)
        IndicadorImpactoValidator._validar_valor_real(valor_real)
        IndicadorImpactoValidator._validar_unicidad_kpi(proyecto_id, kpi_nombre)

    @staticmethod
    def validar_actualizacion(indicador_id, proyecto_id, kpi_nombre, valor_proyectado, valor_real=None):
        IndicadorImpactoValidator._validar_proyecto(proyecto_id)
        IndicadorImpactoValidator._validar_kpi_nombre(kpi_nombre)
        IndicadorImpactoValidator._validar_valor_proyectado(valor_proyectado)
        IndicadorImpactoValidator._validar_valor_real(valor_real)
        IndicadorImpactoValidator._validar_unicidad_kpi(
            proyecto_id, kpi_nombre, excluir_id=indicador_id
        )

    @staticmethod
    def validar_eliminacion(indicador_impacto):
        pass

    @staticmethod
    def validar_valor_real_actualizacion(valor_real):
        """
        Validación exclusiva de la acción de negocio `actualizar_valor_real`.

        A diferencia de `_validar_valor_real` (usada en `crear`/`actualizar`,
        donde `None` significa "omitir, conservar el valor actual"), aquí el
        único propósito de la llamada es fijar ese campo: `None` es un dato
        faltante, no un valor legítimo. Sin esta validación, `None` se
        propagaría hasta `IndicadorImpacto.valor_real` (FloatField no
        nullable) y provocaría un IntegrityError/500 en vez de un 400 claro.
        """
        if valor_real is None:
            raise ValidationError(
                {"valor_real": "El valor real es obligatorio para esta operación."}
            )
        IndicadorImpactoValidator._validar_valor_real(valor_real)

    @staticmethod
    def _validar_proyecto(proyecto_id):
        if not proyecto_id:
            raise ValidationError({"proyecto": "El proyecto es obligatorio."})
        # Import diferido: investigacion_formal no es dependencia directa de crm
        from apps.investigacion_formal.models import Proyecto
        if not Proyecto.objects.filter(pk=proyecto_id).exists():
            raise ValidationError({"proyecto": f"No existe un Proyecto con id={proyecto_id}."})

    @staticmethod
    def _validar_kpi_nombre(kpi_nombre):
        if not kpi_nombre or not kpi_nombre.strip():
            raise ValidationError({"kpi_nombre": "El nombre del KPI es obligatorio."})
        if len(kpi_nombre) > 100:
            raise ValidationError(
                {"kpi_nombre": f"El KPI '{kpi_nombre}' supera el máximo de 100 caracteres."}
            )

    @staticmethod
    def _validar_valor_proyectado(valor_proyectado):
        if valor_proyectado is None:
            raise ValidationError({"valor_proyectado": "El valor proyectado es obligatorio."})
        try:
            float(valor_proyectado)
        except (TypeError, ValueError):
            raise ValidationError({"valor_proyectado": "El valor proyectado debe ser numérico."})

    @staticmethod
    def _validar_valor_real(valor_real):
        if valor_real is None:
            return  # el modelo trae default=0, es válido omitirlo en crear/actualizar
        try:
            float(valor_real)
        except (TypeError, ValueError):
            raise ValidationError({"valor_real": "El valor real debe ser numérico."})

    @staticmethod
    def _validar_unicidad_kpi(proyecto_id, kpi_nombre, excluir_id=None):
        if IndicadorImpactoSelector.existe_kpi_para_proyecto(
            proyecto_id, kpi_nombre, excluir_id=excluir_id
        ):
            raise ValidationError(
                {"kpi_nombre": (
                    f"Ya existe un indicador con el KPI '{kpi_nombre}' "
                    f"registrado para este proyecto."
                )}
            )