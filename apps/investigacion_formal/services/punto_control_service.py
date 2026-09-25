from django.db import transaction

from apps.investigacion_formal.models import PuntoControl
from apps.investigacion_formal.selectors.punto_control_selector import PuntoControlSelector
from apps.investigacion_formal.validators.punto_control_validator import PuntoControlValidator
from apps.common.services.historial_service import HistorialService


class PuntoControlService:

    @staticmethod
    def listar():
        return PuntoControlSelector.listar()

    @staticmethod
    def obtener(punto_control_id):
        return PuntoControlSelector.obtener(punto_control_id)

    @staticmethod
    @transaction.atomic
    def crear(control, peso, ejecutor):
        PuntoControlValidator.validar_creacion(control, peso)
        punto = PuntoControl.objects.create(
            control=control.strip(),
            peso=peso,
            completado=0,
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el punto de control '{punto.control}' (id={punto.pk}).",
            objeto=punto,
        )
        return punto