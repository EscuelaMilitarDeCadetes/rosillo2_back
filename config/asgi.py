"""
ASGI config for rosillo project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from apps.common.middleware_ws import JWTAuthMiddleware
from apps.common.routing import websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})