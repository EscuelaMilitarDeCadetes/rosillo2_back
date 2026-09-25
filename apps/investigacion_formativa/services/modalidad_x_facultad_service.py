# apps/investigacion_formativa/services/modalidad_x_facultad_service.py
from django.db import transaction

from apps.investigacion_formativa.models import ModalidadXFacultad
from apps.investigacion_formativa.selectors.modalidad_x_facultad_selector import (
    ModalidadXFacultadSelector,
)
from apps.investigacion_formativa.validators.modalidad_x_facultad_validator import (
    ModalidadXFacultadValidator,
)
from apps.common.services.historial_service import HistorialService


class ModalidadXFacultadService:

    @staticmethod
    def listar():
        return ModalidadXFacultadSelector.listar()

    @staticmethod
    def obtener(modalidad_x_facultad_id):
        return ModalidadXFacultadSelector.obtener(modalidad_x_facultad_id)

    @staticmethod
    def listar_por_facultad(facultad_id, disponible=None):
        return ModalidadXFacultadSelector.listar_por_facultad(facultad_id, disponible=disponible)

    @staticmethod
    @transaction.atomic
    def crear(facultad_id, modalidad_id, ejecutor, disponible=True):
        ModalidadXFacultadValidator.validar_creacion(facultad_id, modalidad_id, disponible)
        vinculo = ModalidadXFacultad.objects.create(
            facultad_id=facultad_id,
            modalidad_id=modalidad_id,
            disponible=disponible,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se habilitó la modalidad '{vinculo.modalidad.nombre}' para la facultad "
            f"'{vinculo.facultad.nombre_facultad}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def habilitar(modalidad_x_facultad_id, ejecutor):
        vinculo = ModalidadXFacultadSelector.obtener(modalidad_x_facultad_id)
        ModalidadXFacultadValidator.validar_habilitacion(vinculo)
        vinculo.disponible = True
        vinculo.save(update_fields=['disponible'])
        HistorialService.registrar(
            ejecutor,
            f"Se habilitó la modalidad '{vinculo.modalidad.nombre}' para la facultad "
            f"'{vinculo.facultad.nombre_facultad}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def deshabilitar(modalidad_x_facultad_id, ejecutor):
        vinculo = ModalidadXFacultadSelector.obtener(modalidad_x_facultad_id)
        ModalidadXFacultadValidator.validar_deshabilitacion(vinculo)
        vinculo.disponible = False
        vinculo.save(update_fields=['disponible'])
        HistorialService.registrar(
            ejecutor,
            f"Se deshabilitó la modalidad '{vinculo.modalidad.nombre}' para la facultad "
            f"'{vinculo.facultad.nombre_facultad}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo