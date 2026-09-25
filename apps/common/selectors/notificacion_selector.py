from datetime import timedelta

from django.utils import timezone
from apps.common.models import Notificacion


class NotificacionSelector:
    @staticmethod
    def listar():
        return Notificacion.objects.select_related('usuario_destino').all()

    @staticmethod
    def obtener(notificacion_id):
        return Notificacion.objects.select_related('usuario_destino').get(pk=notificacion_id)

    @staticmethod
    def listar_por_usuario(usuario_id, solo_no_leidas=False):
        qs = Notificacion.objects.filter(usuario_destino_id=usuario_id)
        if solo_no_leidas:
            qs = qs.filter(leido=False)
        return qs.order_by('-fecha_creacion')

    @staticmethod
    def existe_recordatorio_hoy(usuario_id, url_relacionada, tipo='alerta'):
        """Evita que el job de recordatorios envíe el mismo aviso más de una
        vez el mismo día para la misma tarea/documento."""
        ahora = timezone.now()
        inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        return Notificacion.objects.filter(
            usuario_destino_id=usuario_id,
            url_relacionada=url_relacionada,
            tipo=tipo,
            fecha_creacion__gte=inicio_dia,
            fecha_creacion__lt=fin_dia,
        ).exists()