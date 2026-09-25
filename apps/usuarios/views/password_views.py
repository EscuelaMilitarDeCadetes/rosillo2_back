from apps.common.services.historial_service import HistorialService
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers.password_serializers import (
    ForgotPasswordSerializer, 
    ResetPasswordSerializer,
    ChangePasswordSerializer
)
from ..services.password_service import PasswordService
from django.core.exceptions import ValidationError as DjangoValidationError



class PasswordViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='forgot-password')
    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            PasswordService.request_password_reset(serializer.validated_data['email'])
            return Response({"message": "Si tu correo está registrado, recibirás un enlace para restablecer tu contraseña."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='reset-password')
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            user = PasswordService.validate_reset_token(token)
            if user:
                try:
                    PasswordService.reset_password(user, serializer.validated_data['password'])
                except DjangoValidationError as e:
                    return Response({"password": e.messages}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)
            return Response({"error": "El token es inválido o ha expirado."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        user = request.user
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["La contraseña actual es incorrecta."]}, status=status.HTTP_400_BAD_REQUEST)        
        # La fortaleza de new_password ya fue validada por el serializer
        # (validate_new_password -> validar_fortaleza_password con user=),
        # no se repite aquí.
        user.set_password(serializer.validated_data['new_password'])
        user.debe_cambiar_password = False
        user.save()
        HistorialService.registrar(user, f"El usuario {user.username} cambió su contraseña.")
        return Response({"message": "Contraseña cambiada exitosamente."}, status=status.HTTP_200_OK)