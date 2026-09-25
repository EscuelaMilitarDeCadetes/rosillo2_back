from django.db import transaction

from apps.investigacion_formativa.models import RegistroHoras
from apps.investigacion_formativa.selectors.registro_horas_selector import RegistroHorasSelector
from apps.investigacion_formativa.validators.registro_horas_validator import RegistroHorasValidator
from apps.common.services.historial_service import HistorialService


class RegistroHorasService:

    @staticmethod
    def listar():
        return RegistroHorasSelector.listar()

    @staticmethod
    def obtener(registro_horas_id):
        return RegistroHorasSelector.obtener(registro_horas_id)

    @staticmethod
    def obtener_por_proceso(proceso_id):
        return RegistroHorasSelector.obtener_por_proceso(proceso_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_id, ejecutor, horas_requeridas=120):
        RegistroHorasValidator.validar_creacion(proceso_id, horas_requeridas)
        control = RegistroHoras.objects.create(
            proceso_id=proceso_id,
            horas_requeridas=horas_requeridas,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el control de horas del proceso '{control.proceso.titulo}' "
            f"(mínimo exigido: {horas_requeridas} h, id={control.pk}).",
            objeto=control,
        )
        return control

    @staticmethod
    @transaction.atomic
    def ajustar_horas_requeridas(registro_horas_id, nuevas_horas_requeridas, ejecutor):
        control = RegistroHorasSelector.obtener(registro_horas_id)
        RegistroHorasValidator.validar_ajuste_horas_requeridas(control, nuevas_horas_requeridas)
        control.horas_requeridas = nuevas_horas_requeridas
        control.cumple_requisito = control.horas_acumuladas >= nuevas_horas_requeridas
        control.save(update_fields=['horas_requeridas', 'cumple_requisito'])
        HistorialService.registrar(
            ejecutor,
            f"Se ajustaron las horas requeridas del proceso '{control.proceso.titulo}' a "
            f"{nuevas_horas_requeridas} h (id={control.pk}).",
            objeto=control,
        )
        return control

    @staticmethod
    @transaction.atomic
    def recalcular(registro_horas_id, ejecutor):
        """Reutiliza RegistroHoras.actualizar() (suma RegistroActividades del proceso)
        y deja el rastro de auditoría que el método del modelo no puede registrar."""
        control = RegistroHorasSelector.obtener(registro_horas_id)
        control.actualizar()
        HistorialService.registrar(
            ejecutor,
            f"Se recalcularon las horas acumuladas del proceso '{control.proceso.titulo}': "
            f"{control.horas_acumuladas}/{control.horas_requeridas} h (id={control.pk}).",
            objeto=control,
        )
        return control