# apps/investigacion_formativa/services/regla_flujo_service.py
from django.db import transaction

from apps.investigacion_formativa.models import ReglaFlujo
from apps.investigacion_formativa.selectors.regla_flujo_selector import ReglaFlujoSelector
from apps.investigacion_formativa.validators.regla_flujo_validator import ReglaFlujoValidator
from apps.common.services.historial_service import HistorialService


class ReglaFlujoService:

    @staticmethod
    def listar():
        return ReglaFlujoSelector.listar()

    @staticmethod
    def obtener(regla_id):
        return ReglaFlujoSelector.obtener(regla_id)

    @staticmethod
    def listar_por_transicion(etapa_origen_id, etapa_destino_id):
        return ReglaFlujoSelector.listar_por_transicion(
            etapa_origen_id, etapa_destino_id
        )

    @staticmethod
    @transaction.atomic
    def crear(etapa_origen_id, etapa_destino_id, nombre, operador, tipo_regla,
              valor_minimo, valor_maximo, mensaje_error, accion_resultado,
              descripcion, fecha_inicio, ejecutor, fecha_fin=None,
              bloqueante=False, prioridad=1):
        ReglaFlujoValidator.validar_creacion(
            etapa_origen_id, etapa_destino_id, nombre, operador, tipo_regla,
            valor_minimo, valor_maximo, mensaje_error, accion_resultado,
            descripcion, fecha_inicio, fecha_fin, bloqueante, prioridad,
        )
        regla = ReglaFlujo.objects.create(
            etapa_origen_id=etapa_origen_id,
            etapa_destino_id=etapa_destino_id,
            nombre=nombre,
            operador=operador,
            tipo_regla=tipo_regla,
            valor_minimo=valor_minimo,
            valor_maximo=valor_maximo,
            mensaje_error=mensaje_error,
            accion_resultado=accion_resultado,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            bloqueante=bloqueante,
            prioridad=prioridad,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó la regla '{regla.nombre}' entre '{regla.etapa_origen.nombre}' y "
            f"'{regla.etapa_destino.nombre}' (id={regla.pk}).",
            objeto=regla,
        )
        return regla

    @staticmethod
    @transaction.atomic
    def actualizar(regla_id, etapa_origen_id, etapa_destino_id, nombre, operador, tipo_regla,
                    valor_minimo, valor_maximo, mensaje_error, accion_resultado,
                    descripcion, fecha_inicio, ejecutor, fecha_fin=None, prioridad=1):
        regla = ReglaFlujoSelector.obtener(regla_id)
        ReglaFlujoValidator.validar_actualizacion(
            regla, etapa_origen_id, etapa_destino_id, nombre, operador, tipo_regla,
            valor_minimo, valor_maximo, mensaje_error, accion_resultado,
            descripcion, fecha_inicio, fecha_fin, prioridad,
        )
        regla.etapa_origen_id = etapa_origen_id
        regla.etapa_destino_id = etapa_destino_id
        regla.nombre = nombre
        regla.operador = operador
        regla.tipo_regla = tipo_regla
        regla.valor_minimo = valor_minimo
        regla.valor_maximo = valor_maximo
        regla.mensaje_error = mensaje_error
        regla.accion_resultado = accion_resultado
        regla.descripcion = descripcion
        regla.fecha_inicio = fecha_inicio
        regla.fecha_fin = fecha_fin
        regla.prioridad = prioridad
        regla.save(update_fields=[
            'etapa_origen', 'etapa_destino', 'nombre', 'operador', 'tipo_regla',
            'valor_minimo', 'valor_maximo', 'mensaje_error', 'accion_resultado',
            'descripcion', 'fecha_inicio', 'fecha_fin', 'prioridad',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la regla '{regla.nombre}' (id={regla.pk}).",
            objeto=regla,
        )
        return regla

    @staticmethod
    @transaction.atomic
    def activar(regla_id, ejecutor):
        regla = ReglaFlujoSelector.obtener(regla_id)
        ReglaFlujoValidator.validar_activacion(regla)
        regla.activa = True
        regla.save(update_fields=['activa'])
        HistorialService.registrar(
            ejecutor,
            f"Se activó la regla '{regla.nombre}' (id={regla.pk}).",
            objeto=regla,
        )
        return regla

    @staticmethod
    @transaction.atomic
    def desactivar(regla_id, ejecutor):
        """
        Único mecanismo de baja para ReglaFlujo.
        """
        regla = ReglaFlujoSelector.obtener(regla_id)
        ReglaFlujoValidator.validar_desactivacion(regla)
        regla.activa = False
        regla.save(update_fields=['activa'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó la regla '{regla.nombre}' (id={regla.pk}).",
            objeto=regla,
        )
        return regla