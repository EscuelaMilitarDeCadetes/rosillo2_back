from apps.usuarios.pagination import UsuariosPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..permissions.es_soporte import EsSoporte
from ..models import RolXUsuario
from ..serializers.rol_x_usuario_serializer import RolXUsuarioSerializer
from ..services.rol_x_usuario_service import RolXUsuarioService

from django.db.models import Prefetch
from apps.usuarios.models import UsuarioXPersona


class RolXUsuarioViewSet(viewsets.ViewSet):
    serializer_class = RolXUsuarioSerializer
    pagination_class = UsuariosPageNumberPagination

    def get_permissions(self):
        permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return (
            RolXUsuario.objects
            .select_related('usuario', 'rol')
            .prefetch_related(
                Prefetch(
                    'usuario__asignaciones',
                    queryset=UsuarioXPersona.objects
                        .filter(estado=True)
                        .select_related('persona', 'persona__grado'),
                )
            )
            .filter(estado=True)
        )        

    def list(self, request):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        rxu = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(self.serializer_class(rxu).data)

    @action(detail=False, methods=['get'], url_path='ver-roles/(?P<usuario_id>[0-9]+)')
    def ver_roles_usuario(self, request, usuario_id=None):
        roles = self.get_queryset().filter(usuario_id=usuario_id)
        return Response(self.serializer_class(roles, many=True).data)

    @action(detail=False, methods=['post'], url_path='agregar-rol')
    def agregar_rol(self, request):
        usuario_id = request.data.get('usuario_id')
        rol_id = request.data.get('rol_id')
        if not usuario_id or not rol_id:
            return Response({"error": "Se requieren 'usuario_id' y 'rol_id'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            rxu = RolXUsuarioService.agregar_rol_a_usuario(
                usuario_id=usuario_id, rol_id=rol_id, ejecutor=request.user
            )
            return Response(self.serializer_class(rxu).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='borrar-rol')
    def borrar_rol(self, request):
        usuario_id = request.data.get('usuario_id')
        rol_id = request.data.get('rol_id')
        if not usuario_id or not rol_id:
            return Response({"error": "Se requieren 'usuario_id' y 'rol_id'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RolXUsuarioService.borrar_rol_de_usuario(
                usuario_id=usuario_id, rol_id=rol_id, ejecutor=request.user
            )
            return Response({"message": "Rol removido correctamente."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar_rol_x_usuario(self, request):
        usuario_id = request.query_params.get('usuario_id')
        rol_id = request.query_params.get('rol_id')
        qs = self.get_queryset().filter(usuario_id=usuario_id, rol_id=rol_id)
        return Response(self.serializer_class(qs, many=True).data)
    
    @action(detail=False, methods=['get'], url_path='historico/(?P<usuario_id>[0-9]+)')
    def historico_roles_usuario(self, request, usuario_id=None):
        roles = RolXUsuarioService.listar_roles_historico_de_usuario(usuario_id=usuario_id)
        return Response(self.serializer_class(roles, many=True).data)