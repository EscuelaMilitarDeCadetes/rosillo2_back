from django.db import transaction

from apps.crm.models import IndicadorImpacto
from apps.crm.selectors.indicador_impacto_selector import IndicadorImpactoSelector
from apps.crm.validators.indicador_impacto_validator import IndicadorImpactoValidator
from apps.common.services.historial_service import HistorialService


class IndicadorImpactoService:

    @staticmethod
    def listar():
        return IndicadorImpactoSelector.listar()

    @staticmethod
    def obtener(indicador_id):
        return IndicadorImpactoSelector.obtener(indicador_id)

    @staticmethod
    @transaction.atomic
    def crear(proyecto_id, kpi_nombre, valor_proyectado, ejecutor, valor_real=None):
        IndicadorImpactoValidator.validar_creacion(
            proyecto_id, kpi_nombre, valor_proyectado, valor_real
        )
        indicador = IndicadorImpacto.objects.create(
            proyecto_id=proyecto_id,
            kpi_nombre=kpi_nombre.strip(),
            valor_proyectado=valor_proyectado,
            valor_real=valor_real if valor_real is not None else 0,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró el indicador de impacto '{indicador.kpi_nombre}' "
            f"para el proyecto id={proyecto_id} "
            f"(valor proyectado={indicador.valor_proyectado}, id={indicador.pk}).",
            objeto=indicador,
        )
        return indicador

    @staticmethod
    @transaction.atomic
    def actualizar(indicador_id, ejecutor, proyecto_id=None, kpi_nombre=None, valor_proyectado=None, valor_real=None):
        indicador = IndicadorImpactoSelector.obtener(indicador_id)

        nuevo_proyecto_id = proyecto_id if proyecto_id is not None else indicador.proyecto_id
        nuevo_kpi_nombre = kpi_nombre if kpi_nombre is not None else indicador.kpi_nombre
        nuevo_valor_proyectado = (
            valor_proyectado if valor_proyectado is not None else indicador.valor_proyectado
        )
        nuevo_valor_real = valor_real if valor_real is not None else indicador.valor_real

        IndicadorImpactoValidator.validar_actualizacion(
            indicador_id, nuevo_proyecto_id, nuevo_kpi_nombre,
            nuevo_valor_proyectado, nuevo_valor_real,
        )

        indicador.proyecto_id = nuevo_proyecto_id
        indicador.kpi_nombre = nuevo_kpi_nombre.strip()
        indicador.valor_proyectado = nuevo_valor_proyectado
        indicador.valor_real = nuevo_valor_real
        indicador.save(update_fields=["proyecto", "kpi_nombre", "valor_proyectado", "valor_real"])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el indicador de impacto '{indicador.kpi_nombre}' "
            f"del proyecto id={indicador.proyecto_id} (id={indicador.pk}).",
            objeto=indicador,
        )
        return indicador

    @staticmethod
    @transaction.atomic
    def actualizar_valor_real(indicador_id, nuevo_valor_real, ejecutor):
        """Atajo de negocio: solo actualiza el avance (valor_real),
        sin tocar la meta (valor_proyectado) ni reasignar el proyecto/KPI."""
        indicador = IndicadorImpactoSelector.obtener(indicador_id)
        IndicadorImpactoValidator.validar_valor_real_actualizacion(nuevo_valor_real)
        valor_anterior = indicador.valor_real
        indicador.valor_real = nuevo_valor_real
        indicador.save(update_fields=["valor_real"])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el avance del indicador '{indicador.kpi_nombre}' "
            f"(proyecto id={indicador.proyecto_id}) de {valor_anterior} a "
            f"{nuevo_valor_real} (id={indicador.pk}).",
            objeto=indicador,
        )
        return indicador

    @staticmethod
    @transaction.atomic
    def eliminar(indicador_id, ejecutor):
        indicador = IndicadorImpactoSelector.obtener(indicador_id)
        IndicadorImpactoValidator.validar_eliminacion(indicador)
        descripcion = (
            f"Se eliminó el indicador de impacto '{indicador.kpi_nombre}' "
            f"del proyecto id={indicador.proyecto_id} (id={indicador.pk})."
        )
        HistorialService.registrar(ejecutor, descripcion)
        indicador.delete()
        return True

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return IndicadorImpactoSelector.listar_por_proyecto(proyecto_id)

    @staticmethod
    def obtener_por_proyecto_y_kpi(proyecto_id, kpi_nombre):
        return IndicadorImpactoSelector.obtener_por_proyecto_y_kpi(proyecto_id, kpi_nombre)