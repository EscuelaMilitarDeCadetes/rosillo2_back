from apps.common.pagination import CommonPageNumberPagination
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.usuarios.permissions.es_supervisor import EsSupervisor
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.common.serializers import NotificacionSerializer
from apps.common.services.notificacion_service import NotificacionService


class NotificacionViewSet(viewsets.ViewSet):
    serializer_class = NotificacionSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_lectura_ampliada = ['list', 'retrieve']
        acciones_autoservicio = ['por_usuario', 'marcar_leida', 'marcar_todas_leidas']
        if self.action in acciones_lectura_ampliada:
            permission_classes = [EsSoporte | EsSupervisor]
        elif self.action in acciones_autoservicio:
            permission_classes = [IsAuthenticated]
        else:  # create, destroy, enviar_recordatorios (cubierto aparte con IsAdminUser)
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        notificaciones = NotificacionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(notificaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        notificacion = NotificacionService.obtener(pk)
        return Response(self.serializer_class(notificacion).data)

    def create(self, request):
        notificacion = NotificacionService.crear(
            usuario_destino_id=request.data.get("usuario_destino"),
            mensaje=request.data.get("mensaje"),
            tipo=request.data.get("tipo"),
            url_relacionada=request.data.get("url_relacionada"),
            notificar_email=request.data.get("notificar_email", False),
        )
        return Response(self.serializer_class(notificacion).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        NotificacionService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="marcar-leida")
    def marcar_leida(self, request, pk=None):
        notificacion = NotificacionService.obtener(pk)
        if notificacion.usuario_destino_id != request.user.pk and not request.user.has_role('SOPORTE'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        notificacion = NotificacionService.marcar_leida(pk)
        return Response(self.serializer_class(notificacion).data)

    @action(detail=False, methods=["post"], url_path="marcar-todas-leidas")
    def marcar_todas_leidas(self, request):
        usuario_id = request.data.get("usuario_destino", request.user.pk)
        if str(usuario_id) != str(request.user.pk) and not request.user.has_role('SOPORTE'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        cantidad = NotificacionService.marcar_todas_leidas(usuario_id)
        return Response({"actualizadas": cantidad})

    @action(detail=False, methods=["get"], url_path="por-usuario/(?P<usuario_id>[^/.]+)")
    def por_usuario(self, request, usuario_id=None):
        if str(request.user.pk) != str(usuario_id) and not request.user.has_role('SOPORTE'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        solo_no_leidas = request.query_params.get("solo_no_leidas", "false").lower() == "true"
        notificaciones = NotificacionService.listar_por_usuario(usuario_id, solo_no_leidas=solo_no_leidas)
        return Response(self.serializer_class(notificaciones, many=True).data)

    @action(
        detail=False, methods=["post"], url_path="enviar-recordatorios",
        permission_classes=[permissions.IsAdminUser],
    )
    def enviar_recordatorios(self, request):
        dias = int(request.data.get("dias_anticipacion", 3))
        creadas = NotificacionService.enviar_recordatorios_tareas(dias_anticipacion=dias)
        return Response({"notificaciones_creadas": len(creadas)})