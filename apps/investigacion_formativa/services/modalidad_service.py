from django.db import transaction

from apps.investigacion_formativa.models import Modalidad
from apps.investigacion_formativa.selectors.modalidad_selector import ModalidadSelector
from apps.investigacion_formativa.validators.modalidad_validator import ModalidadValidator
from apps.common.services.historial_service import HistorialService


class ModalidadService:

    @staticmethod
    def listar():
        return ModalidadSelector.listar()

    @staticmethod
    def obtener(modalidad_id):
        return ModalidadSelector.obtener(modalidad_id)

    @staticmethod
    def listar_activas():
        return ModalidadSelector.listar_activas()

    @staticmethod
    @transaction.atomic
    def crear(nombre, codigo, ejecutor, descripcion=None, requiere_evaluadores=False,
              requiere_tutor=None, requiere_antiplagio=None, requiere_sustentacion=None,
              cantidad_maxima_estudiantes=None, cantidad_minima_evaluadores=None,
              permite_homologacion=None, requiere_producto_final=None):
        ModalidadValidator.validar_creacion(
            nombre, codigo, descripcion, requiere_evaluadores, requiere_tutor,
            requiere_antiplagio, requiere_sustentacion, cantidad_maxima_estudiantes,
            cantidad_minima_evaluadores, permite_homologacion, requiere_producto_final,
        )
        modalidad = Modalidad.objects.create(
            nombre=nombre,
            codigo=codigo,
            descripcion=descripcion,
            requiere_evaluadores=requiere_evaluadores,
            requiere_tutor=requiere_tutor,
            requiere_antiplagio=requiere_antiplagio,
            requiere_sustentacion=requiere_sustentacion,
            cantidad_maxima_estudiantes=cantidad_maxima_estudiantes,
            cantidad_minima_evaluadores=cantidad_minima_evaluadores,
            permite_homologacion=permite_homologacion,
            requiere_producto_final=requiere_producto_final,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó la modalidad '{modalidad.nombre}' (id={modalidad.pk}).",
            objeto=modalidad,
        )
        return modalidad

    @staticmethod
    @transaction.atomic
    def actualizar(modalidad_id, nombre, codigo, ejecutor, descripcion=None,
                    requiere_evaluadores=False, requiere_tutor=None, requiere_antiplagio=None,
                    requiere_sustentacion=None, cantidad_maxima_estudiantes=None,
                    cantidad_minima_evaluadores=None, permite_homologacion=None,
                    requiere_producto_final=None):
        modalidad = ModalidadSelector.obtener(modalidad_id)
        ModalidadValidator.validar_actualizacion(
            modalidad, nombre, codigo, descripcion, requiere_evaluadores, requiere_tutor,
            requiere_antiplagio, requiere_sustentacion, cantidad_maxima_estudiantes,
            cantidad_minima_evaluadores, permite_homologacion, requiere_producto_final,
        )
        modalidad.nombre = nombre
        modalidad.codigo = codigo
        modalidad.descripcion = descripcion
        modalidad.requiere_evaluadores = requiere_evaluadores
        modalidad.requiere_tutor = requiere_tutor
        modalidad.requiere_antiplagio = requiere_antiplagio
        modalidad.requiere_sustentacion = requiere_sustentacion
        modalidad.cantidad_maxima_estudiantes = cantidad_maxima_estudiantes
        modalidad.cantidad_minima_evaluadores = cantidad_minima_evaluadores
        modalidad.permite_homologacion = permite_homologacion
        modalidad.requiere_producto_final = requiere_producto_final
        modalidad.save(update_fields=[
            'nombre', 'codigo', 'descripcion', 'requiere_evaluadores', 'requiere_tutor',
            'requiere_antiplagio', 'requiere_sustentacion', 'cantidad_maxima_estudiantes',
            'cantidad_minima_evaluadores', 'permite_homologacion', 'requiere_producto_final',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la modalidad '{modalidad.nombre}' (id={modalidad.pk}).",
            objeto=modalidad,
        )
        return modalidad

    @staticmethod
    @transaction.atomic
    def activar(modalidad_id, ejecutor):
        modalidad = ModalidadSelector.obtener(modalidad_id)
        ModalidadValidator.validar_activacion(modalidad)
        modalidad.activo = True
        modalidad.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se activó la modalidad '{modalidad.nombre}' (id={modalidad.pk}).",
            objeto=modalidad,
        )
        return modalidad

    @staticmethod
    @transaction.atomic
    def eliminar(modalidad_id, ejecutor):
        modalidad = ModalidadSelector.obtener(modalidad_id)
        ModalidadValidator.validar_eliminacion(modalidad)
        modalidad.activo = False
        modalidad.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) la modalidad '{modalidad.nombre}' (id={modalidad.pk}).",
            objeto=modalidad,
        )
        return modalidad