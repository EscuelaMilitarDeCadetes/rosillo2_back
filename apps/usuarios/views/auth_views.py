from apps.usuarios.serializers.login_serializer import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.common.services.historial_service import HistorialService
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from apps.usuarios.throttles import LoginRateThrottle
from apps.usuarios.ambitos import (
    AMBITO_FORMAL, AMBITO_FORMATIVA, usuario_tiene_acceso_a_ambito,
)


class AmbitoLoginView(APIView):
    """
    Base de los dos endpoints de login (formal / formativa). No se expone
    directamente: LoginFormalView y LoginFormativaView fijan `ambito`.

    Emite un JWT con el claim 'ambito' embebido (se copia automáticamente
    del refresh al access token, y sobrevive a la rotación de refresh
    tokens porque ROTATE_REFRESH_TOKENS reutiliza el mismo payload, no
    genera uno nuevo desde cero — ver config/settings/base.py).

    Antes de emitir el token se valida que el usuario tenga al menos un rol
    activo permitido en ese ámbito (ver apps/usuarios/ambitos.py); un
    usuario con rol exclusivo del otro ámbito (p. ej. Estudiante intentando
    entrar por el login de formal) recibe 403, no un token que luego
    fallaría en cada endpoint.
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    ambito = None  # AMBITO_FORMAL o AMBITO_FORMATIVA, fijado por subclase

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request=request, username=username, password=password)

        if user is None:
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not usuario_tiene_acceso_a_ambito(user, self.ambito):
            return Response(
                {"error": "Su rol no tiene acceso a este módulo."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        refresh['ambito'] = self.ambito

        HistorialService.registrar(
            user, f"Inicio de sesión exitoso ({self.ambito})."
        )

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "ambito": self.ambito,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            # el frontend usa este flag para forzar la redirección
            # a change-password antes de permitir el resto de la navegación
            "debe_cambiar_password": user.debe_cambiar_password,
        })


class LoginFormalView(AmbitoLoginView):
    ambito = AMBITO_FORMAL


class LoginFormativaView(AmbitoLoginView):
    ambito = AMBITO_FORMATIVA


class LogoutView(APIView):
    """
    Endpoint para cerrar sesión y anular el Refresh Token.
    Ámbito-agnóstico a propósito: cierra la sesión sin importar por cuál
    de los dos logins se entró, porque blacklistea el refresh token
    concreto que se envía, no un tipo de sesión.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Se requiere el refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            HistorialService.registrar(request.user, "Cierre de sesión exitoso.")
            return Response({"message": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Token inválido o ya expirado."}, status=status.HTTP_400_BAD_REQUEST)