from apps.institucional.pagination import InstitucionalPageNumberPagination
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.institucional.serializers import FacultadXGrupoSerializer
from apps.institucional.services.facultad_x_grupo_service import FacultadXGrupoService


class FacultadXGrupoViewSet(viewsets.ViewSet):
    """
    Adaptador HTTP puro: toda la lógica vive en FacultadXGrupoService.
    Sin destroy(): tabla estructural permanente.
    """
    serializer_class = FacultadXGrupoSerializer
    pagination_class = InstitucionalPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        relaciones = FacultadXGrupoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(relaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        relacion = FacultadXGrupoService.obtener(pk)
        serializer = self.serializer_class(relacion)
        return Response(serializer.data)

    def create(self, request):
        relacion = FacultadXGrupoService.crear(
            grupo_id=request.data.get("grupo"),
            facultad_id=request.data.get("facultad"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(relacion)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        relacion = FacultadXGrupoService.actualizar(
            facultad_x_grupo_id=pk,
            grupo_id=request.data.get("grupo"),
            facultad_id=request.data.get("facultad"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(relacion)
        return Response(serializer.data)