from datetime import timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from apps.common.models import Tarea


class TareaSelector:
    @staticmethod
    def listar():
        return Tarea.objects.select_related('asignado_a', 'content_type').all()

    @staticmethod
    def obtener(tarea_id):
        return Tarea.objects.select_related('asignado_a', 'content_type').get(pk=tarea_id)

    @staticmethod
    def listar_por_usuario(usuario_id, solo_pendientes=False):
        qs = Tarea.objects.filter(asignado_a_id=usuario_id)
        if solo_pendientes:
            qs = qs.filter(completada=False)
        return qs.order_by('fecha_limite')

    @staticmethod
    def listar_por_objeto(objeto):
        content_type = ContentType.objects.get_for_model(objeto)
        return (
            Tarea.objects
            .select_related('asignado_a')
            .filter(content_type=content_type, object_id=objeto.pk)
            .order_by('-fecha_creacion')
        )

    @staticmethod
    def listar_vencidas():
        return (
            Tarea.objects
            .select_related('asignado_a')
            .filter(completada=False, fecha_limite__lt=timezone.now().date())
        )

    @staticmethod
    def listar_proximas_a_vencer(dias=3):
        hoy = timezone.now().date()
        return (
            Tarea.objects
            .select_related('asignado_a')
            .filter(
                completada=False,
                fecha_limite__gte=hoy,
                fecha_limite__lte=hoy + timedelta(days=dias),
            )
        )