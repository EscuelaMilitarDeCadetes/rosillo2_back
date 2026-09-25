from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.institucional.serializers import RolGrupoSerializer
from apps.institucional.services.rol_grupo_service import RolGrupoService
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.institucional.pagination import InstitucionalPageNumberPagination


class RolGrupoViewSet(viewsets.ViewSet):
    serializer_class = RolGrupoSerializer
    pagination_class = InstitucionalPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        roles = RolGrupoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(roles, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        rol = RolGrupoService.obtener(pk)
        serializer = self.serializer_class(rol)
        return Response(serializer.data)

    def create(self, request):
        rol = RolGrupoService.crear(
            cargo=request.data.get("cargo"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(rol)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        rol = RolGrupoService.actualizar(
            rol_grupo_id=pk,
            cargo=request.data.get("cargo"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(rol)
        return Response(serializer.data)