from apps.institucional.pagination import InstitucionalPageNumberPagination
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.institucional.serializers import GrupoInvestigacionSerializer
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.institucional.services.grupo_investigacion_service import GrupoInvestigacionService
from apps.institucional.selectors.grupo_investigacion_selector import GrupoXUsuarioAmbiguoError


class GrupoInvestigacionViewSet(viewsets.ViewSet):
    serializer_class = GrupoInvestigacionSerializer
    pagination_class = InstitucionalPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'por_usuario']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        grupos = GrupoInvestigacionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(grupos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        grupo = GrupoInvestigacionService.obtener(pk)
        serializer = self.serializer_class(grupo)
        return Response(serializer.data)

    def create(self, request):
        grupo = GrupoInvestigacionService.crear(
            nombre_grupo=request.data.get("nombre_grupo"),
            sigla_grupo=request.data.get("sigla_grupo"),
            clasificacion_grupo=request.data.get("clasificacion_grupo"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(grupo)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        grupo = GrupoInvestigacionService.actualizar(
            grupo_id=pk,
            nombre_grupo=request.data.get("nombre_grupo"),
            sigla_grupo=request.data.get("sigla_grupo"),
            clasificacion_grupo=request.data.get("clasificacion_grupo"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(grupo)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-usuario/(?P<usuario_id>[^/.]+)")
    def por_usuario(self, request, usuario_id=None):
        try:
            grupo = GrupoInvestigacionService.listar_grupos_usuario(usuario_id)
        except GrupoXUsuarioAmbiguoError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        if grupo is None:
            return Response(status=204)
        serializer = self.serializer_class(grupo)
        return Response(serializer.data)