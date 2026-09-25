#apps/common/middleware_ws.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import logging

Usuario = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def obtener_usuario_desde_token(token):
    try:
        access = AccessToken(token)
        return Usuario.objects.get(id=access['user_id'])
    except Exception as e:
        logger.warning(f"WS JWT auth falló: {type(e).__name__}: {e}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]
        scope["user"] = await obtener_usuario_desde_token(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)