from apps.institucional.pagination import InstitucionalPageNumberPagination
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.institucional.serializers import FacultadEscuelaSerializer
from apps.institucional.services.facultad_escuela_service import FacultadEscuelaService
from apps.institucional.selectors.facultad_escuela_selector import FacultadXUsuarioAmbiguoError


class FacultadEscuelaViewSet(viewsets.ViewSet):
    serializer_class = FacultadEscuelaSerializer
    pagination_class = InstitucionalPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'por_usuario', 'por_grupo']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        facultades = FacultadEscuelaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(facultades, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        facultad = FacultadEscuelaService.obtener(pk)
        serializer = self.serializer_class(facultad)
        return Response(serializer.data)

    def create(self, request):
        facultad = FacultadEscuelaService.crear(
            nombre_facultad=request.data.get("nombre_facultad"),
            abreviatura=request.data.get("abreviatura"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(facultad)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        facultad = FacultadEscuelaService.actualizar(
            facultad_id=pk,
            nombre_facultad=request.data.get("nombre_facultad"),
            abreviatura=request.data.get("abreviatura"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(facultad)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-usuario/(?P<usuario_id>[^/.]+)")
    def por_usuario(self, request, usuario_id=None):
        try:
            facultad = FacultadEscuelaService.listar_facultades_usuario(usuario_id)
        except FacultadXUsuarioAmbiguoError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        if facultad is None:
            return Response(status=204)
        serializer = self.serializer_class(facultad)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-grupo")
    def por_grupo(self, request):
        grupo_id = request.query_params.get("grupo_id")
        grupo_id = int(grupo_id) if grupo_id is not None else None
        facultades = FacultadEscuelaService.listar_facultades_grupo(grupo_id)
        serializer = self.serializer_class(facultades, many=True)
        return Response(serializer.data)