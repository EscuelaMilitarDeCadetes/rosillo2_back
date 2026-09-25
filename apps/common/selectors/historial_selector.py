# apps/common/selectors/historial_selector.py
from django.contrib.contenttypes.models import ContentType
from apps.common.models import Historial


class HistorialSelector:
    @staticmethod
    def listar():
        return Historial.objects.select_related('usuario', 'content_type').all()

    @staticmethod
    def obtener(historial_id):
        return Historial.objects.select_related('usuario', 'content_type').get(pk=historial_id)

    @staticmethod
    def buscar(historial_id):
        return Historial.objects.select_related('usuario', 'content_type').filter(pk=historial_id).first()

    @staticmethod
    def listar_por_usuario(usuario_id):
        return Historial.objects.filter(usuario_id=usuario_id).order_by('-fecha_creacion')

    @staticmethod
    def listar_acciones_sistema():
        # Registros creados por signals u otros procesos sin usuario asociado
        return Historial.objects.filter(usuario__isnull=True).order_by('-fecha_creacion')

    @staticmethod
    def listar_por_objeto(objeto):
        content_type = ContentType.objects.get_for_model(objeto)
        return (
            Historial.objects
            .select_related('usuario')
            .filter(content_type=content_type, object_id=objeto.pk)
            .order_by('-fecha_creacion')
        )

    @staticmethod
    def listar_por_modelo(modelo_clase):
        content_type = ContentType.objects.get_for_model(modelo_clase)
        return (
            Historial.objects
            .select_related('usuario')
            .filter(content_type=content_type)
            .order_by('-fecha_creacion')
        )

    @staticmethod
    def listar_por_rango_fechas(fecha_inicio, fecha_fin):
        return (
            Historial.objects
            .select_related('usuario')
            .filter(fecha_creacion__range=(fecha_inicio, fecha_fin))
            .order_by('-fecha_creacion')
        )

    @staticmethod
    def buscar_por_accion(texto):
        return (
            Historial.objects
            .select_related('usuario')
            .filter(accion__icontains=texto)
            .order_by('-fecha_creacion')
        )
        
    @staticmethod
    def buscar_con_filtros(texto=None, usuario_id=None, fecha_inicio=None,
                            fecha_fin=None, solo_sistema=False):
        """
        Combina en una sola consulta lo que antes eran 3 acciones separadas
        (buscar, por_usuario, por_rango_fechas). Todos los filtros son
        opcionales y se aplican en conjunto (AND), no exclusivos entre sí.
        """
        qs = Historial.objects.select_related('usuario', 'content_type').all()
        if texto:
            qs = qs.filter(accion__icontains=texto)
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)
        if solo_sistema:
            qs = qs.filter(usuario__isnull=True)
        if fecha_inicio and fecha_fin:
            qs = qs.filter(fecha_creacion__range=(fecha_inicio, fecha_fin))
        return qs.order_by('-fecha_creacion')