# apps/usuarios/services/password_service.py
import secrets
from datetime import timedelta
from django.utils import timezone
from apps.common.services.email_service import EmailService
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth.password_validation import validate_password
from apps.common.services.historial_service import HistorialService
from django.db import transaction

User = get_user_model()

class PasswordService:

    TOKEN_EXPIRATION_HOURS = 1 # El token expira en 1 hora

    @staticmethod
    @transaction.atomic
    def request_password_reset(email: str):
        """
        Genera un token de reseteo, lo guarda en el usuario y envía el correo.
        """
        try:
            user = User.objects.get(email=email)
            token = secrets.token_urlsafe(32)
            user.token_recuperacion = token
            user.token_creado_en = timezone.now()
            user.save()
            # Construir el link para el frontend (React)
            link = f"{settings.FRONTEND_URL}/reset-password?token={token}"            
            # Enviar correo
            subject = 'Restablecimiento de contraseña'
            message = f'Para restablecer tu contraseña, haz click en el siguiente enlace: {link}\n\nEl enlace expirará en {PasswordService.TOKEN_EXPIRATION_HOURS} hora.'
            EmailService.enviar(subject=subject, message=message, recipient_list=[user.email])
            # Al ser anónimo, podemos registrar al usuario afectado como el "ejecutor" o manejarlo nulo
            HistorialService.registrar(user, f"Se realiza la petición de restablecimiento de contraseña para el usuario {user.username}")
            return True
        except User.DoesNotExist:
            # No revelamos si el usuario existe o no por seguridad
            return False

    @staticmethod
    def validate_reset_token(token: str) -> User | None:
        """
        Valida un token y comprueba que no haya expirado.
        Devuelve el usuario si es válido, de lo contrario None.
        """
        try:
            user = User.objects.get(token_recuperacion=token)            
            if user.token_creado_en:
                expiration_time = user.token_creado_en + timedelta(hours=PasswordService.TOKEN_EXPIRATION_HOURS)
                if timezone.now() > expiration_time:
                    return None # Token expirado            
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def reset_password(user: User, new_password: str):
        """
        Establece la nueva contraseña para un usuario y limpia los campos del token.
        """
        validate_password(new_password, user=user)
        user.set_password(new_password)
        user.token_recuperacion = None
        user.token_creado_en = None
        user.debe_cambiar_password = False  # se limpia también en este flujo
        # Por seguridad, invalidamos todas las sesiones activas al cambiar la contraseña
        tokens_activos = OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)
        for token in tokens_activos:
            BlacklistedToken.objects.get_or_create(token=token)
        HistorialService.registrar(user, f"Solicitud de restablecimiento de contraseña aprobada para el usuario {user.username}")
        user.save()