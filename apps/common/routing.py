from django.urls import re_path
from apps.common.consumers import NotificacionConsumer

websocket_urlpatterns = [
    re_path(r'ws/notificaciones/$', NotificacionConsumer.as_asgi()),
]