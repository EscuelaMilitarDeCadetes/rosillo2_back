from apps.usuarios.pagination import UsuariosPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ..models import UsuarioXPersona
from ..permissions.es_soporte import EsSoporte
from django.http import Http404
from apps.usuarios.services.usuario_facade import UsuarioFacade
from ..serializers.usuario_x_persona_serializers import UsuarioXPersonaSerializer
from django.utils.dateparse import parse_date

User = get_user_model()


class UsuarioXPersonaViewSet(viewsets.ViewSet):
    serializer_class = UsuarioXPersonaSerializer
    pagination_class = UsuariosPageNumberPagination

    def get_permissions(self):
        permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return UsuarioXPersona.objects.select_related('usuario', 'persona').filter(estado=True)

    def list(self, request):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            asignacion = self.get_queryset().get(usuario__id=pk)
            return Response(self.serializer_class(asignacion).data, status=status.HTTP_200_OK)
        except UsuarioXPersona.DoesNotExist:
            return Response({"error": "Asignación no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='historico')
    def historico(self, request, pk=None):
        asignaciones = (
            UsuarioXPersona.objects
            .select_related('usuario', 'persona')
            .filter(usuario_id=pk)
            .order_by('-fecha_inicio')
        )
        return Response(self.serializer_class(asignaciones, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='reasignar')
    def reasignar(self, request):
        usuario_id = request.data.get('usuario_id')
        persona_id = request.data.get('persona_id')
        if not usuario_id or not persona_id:
            return Response({"error": "Se requieren 'usuario_id' y 'persona_id'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            asignacion = UsuarioFacade.service().reasignar_persona_a_usuario(
                usuario_id=usuario_id,
                nueva_persona_id=persona_id,
                ejecutor=request.user
            )
            return Response(
                {"message": f"Usuario {asignacion.usuario.username} reasignado exitosamente a {asignacion.persona.nombre}."},
                status=status.HTTP_200_OK
            )
        except Http404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            detalle = e.detail if hasattr(e, 'detail') else str(e)
            return Response({"error": detalle}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='rotaciones')
    def rotaciones(self, request):
        desde_raw = request.query_params.get('desde')
        hasta_raw = request.query_params.get('hasta')
        queryset = UsuarioXPersona.objects.select_related('usuario', 'persona').order_by('-fecha_inicio')
        if desde_raw:
            desde = parse_date(desde_raw)
            if desde is None:
                return Response({"error": "El parámetro 'desde' debe tener formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(fecha_inicio__date__gte=desde)
        if hasta_raw:
            hasta = parse_date(hasta_raw)
            if hasta is None:
                return Response({"error": "El parámetro 'hasta' debe tener formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(fecha_inicio__date__lte=hasta)
        return Response(self.serializer_class(queryset, many=True).data, status=status.HTTP_200_OK)