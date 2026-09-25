# apps/common/services/historial_service.py
from django.utils import timezone
from ..models import Historial
from django.contrib.contenttypes.models import ContentType
from apps.common.selectors.historial_selector import HistorialSelector
from apps.common.validators.historial_validator import HistorialValidator


class HistorialService:
    @staticmethod
    def registrar(usuario, descripcion, objeto=None):
        HistorialValidator.validar_creacion(descripcion)
        content_type = None
        object_id = None
        if objeto is not None:
            content_type = ContentType.objects.get_for_model(objeto)
            object_id = objeto.pk
        return Historial.objects.create(
            usuario=usuario,
            accion=descripcion,
            fecha_creacion=timezone.now(),
            content_type=content_type,
            object_id=object_id,
        )

    @staticmethod
    def listar():
        return HistorialSelector.listar()

    @staticmethod
    def obtener(historial_id):
        return HistorialSelector.obtener(historial_id)

    @staticmethod
    def buscar(historial_id):
        return HistorialSelector.buscar(historial_id)

    @staticmethod
    def listar_por_usuario(usuario_id):
        return HistorialSelector.listar_por_usuario(usuario_id)

    @staticmethod
    def listar_acciones_sistema():
        return HistorialSelector.listar_acciones_sistema()

    @staticmethod
    def listar_por_objeto(objeto):
        return HistorialSelector.listar_por_objeto(objeto)

    @staticmethod
    def listar_por_modelo(modelo_clase):
        return HistorialSelector.listar_por_modelo(modelo_clase)

    @staticmethod
    def listar_por_rango_fechas(fecha_inicio, fecha_fin):
        return HistorialSelector.listar_por_rango_fechas(fecha_inicio, fecha_fin)

    @staticmethod
    def buscar_por_accion(texto):
        return HistorialSelector.buscar_por_accion(texto)

    @staticmethod
    def buscar_con_filtros(filtros):
        return HistorialSelector.buscar_con_filtros(
            texto=filtros.get("texto"),
            usuario_id=filtros.get("usuario_id"),
            fecha_inicio=filtros.get("fecha_inicio"),
            fecha_fin=filtros.get("fecha_fin"),
            solo_sistema=filtros.get("solo_sistema", False),
        )