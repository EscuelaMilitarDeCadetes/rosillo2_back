from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.common.serializers.soporte_serializer import SoporteSolicitudSerializer
from apps.common.services.soporte_service import SoporteService


class SoporteViewSet(viewsets.ViewSet):
    """
    Cualquier usuario autenticado (todos los roles) puede contactar a
    soporte — no hay restricción de rol en el Thymeleaf original.
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = SoporteSolicitudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        SoporteService.enviar_solicitud(
            usuario=request.user,
            asunto=serializer.validated_data["asunto"],
            mensaje=serializer.validated_data["mensaje"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)