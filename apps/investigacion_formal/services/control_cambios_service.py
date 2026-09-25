from django.db import transaction
from django.utils import timezone

from apps.investigacion_formal.models import ControlCambios
from apps.investigacion_formal.selectors.control_cambios_selector import ControlCambiosSelector
from apps.investigacion_formal.validators.control_cambios_validator import ControlCambiosValidator
from apps.common.services.historial_service import HistorialService


class ControlCambiosService:

    @staticmethod
    def listar():
        return ControlCambiosSelector.listar()

    @staticmethod
    def obtener(control_cambios_id):
        return ControlCambiosSelector.obtener(control_cambios_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return ControlCambiosSelector.listar_por_proyecto(proyecto_id)

    @staticmethod
    @transaction.atomic
    def crear(proyecto_id, tipo_cambio, ejecutor, cambio_tiempo=False, cambio_investigador=False,
              cambio_costo=False, cambio_producto=False, fecha_cambio=None):
        ControlCambiosValidator.validar_creacion(
            proyecto_id, tipo_cambio, fecha_cambio,
            cambio_tiempo, cambio_investigador, cambio_costo, cambio_producto,
        )
        control = ControlCambios.objects.create(
            proyecto_id=proyecto_id,
            tipo_cambio=tipo_cambio.strip(),
            fecha_cambio=fecha_cambio or timezone.now().date(),
            cambio_tiempo=cambio_tiempo,
            cambio_investigador=cambio_investigador,
            cambio_costo=cambio_costo,
            cambio_producto=cambio_producto,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró un control de cambios ('{control.tipo_cambio}') para el "
            f"proyecto id={proyecto_id} (id={control.pk}).",
            objeto=control,
        )
        return control

    @staticmethod
    @transaction.atomic
    def actualizar_banderas(control_cambios_id, ejecutor, cambio_tiempo=None,
                             cambio_investigador=None, cambio_costo=None, cambio_producto=None):
        """Único cambio permitido sobre un registro ya creado: alternar las 4
        banderas. El resto del registro (proyecto, tipo_cambio, fecha_cambio)
        es append-only."""
        control = ControlCambiosSelector.obtener(control_cambios_id)

        nuevo_tiempo = cambio_tiempo if cambio_tiempo is not None else control.cambio_tiempo
        nuevo_investigador = (
            cambio_investigador if cambio_investigador is not None else control.cambio_investigador
        )
        nuevo_costo = cambio_costo if cambio_costo is not None else control.cambio_costo
        nuevo_producto = cambio_producto if cambio_producto is not None else control.cambio_producto

        ControlCambiosValidator.validar_actualizacion_banderas(
            nuevo_tiempo, nuevo_investigador, nuevo_costo, nuevo_producto
        )

        control.cambio_tiempo = nuevo_tiempo
        control.cambio_investigador = nuevo_investigador
        control.cambio_costo = nuevo_costo
        control.cambio_producto = nuevo_producto
        control.save(update_fields=[
            'cambio_tiempo', 'cambio_investigador', 'cambio_costo', 'cambio_producto',
        ])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizaron las banderas del control de cambios id={control.pk} "
            f"del proyecto '{control.proyecto.titulo}' "
            f"(tiempo={nuevo_tiempo}, investigador={nuevo_investigador}, "
            f"costo={nuevo_costo}, producto={nuevo_producto}).",
            objeto=control,
        )
        return control