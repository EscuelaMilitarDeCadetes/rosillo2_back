from apps.common.pagination import CommonPageNumberPagination
from apps.common.ambito import investigacion_visible
from apps.usuarios.permissions.es_soporte import EsSoporte
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.common.serializers import TipoDocumentoSerializer
from apps.common.services.tipo_documento_service import TipoDocumentoService


class TipoDocumentoViewSet(viewsets.ViewSet):
    serializer_class = TipoDocumentoSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_autoservicio = ['list', 'retrieve', 'por_grupo']
        if self.action in acciones_autoservicio:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        tipos = TipoDocumentoService.listar(investigacion=investigacion_visible(request))
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tipos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        tipo = TipoDocumentoService.obtener(pk)
        return Response(self.serializer_class(tipo).data)

    def create(self, request):
        tipo = TipoDocumentoService.crear(
            nombre_documento=request.data.get("nombre_documento"),
            grupo=request.data.get("grupo"),
            investigacion=request.data.get("investigacion"),
            es_obligatorio=request.data.get("es_obligatorio", False),
            ejecutor=request.user
        )
        return Response(self.serializer_class(tipo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        actual = TipoDocumentoService.obtener(pk)
        tipo = TipoDocumentoService.actualizar(
            tipo_documento_id=pk,
            nombre_documento=request.data.get("nombre_documento"),
            grupo=request.data.get("grupo"),
            investigacion=request.data.get("investigacion", actual.investigacion),
            es_obligatorio=request.data.get("es_obligatorio", actual.es_obligatorio),
            ejecutor=request.user
        )
        return Response(self.serializer_class(tipo).data)

    @action(detail=False, methods=["get"], url_path="por-grupo")
    def por_grupo(self, request):
        grupo = request.query_params.get("grupo")
        tipos = TipoDocumentoService.listar_por_grupo(grupo, investigacion=investigacion_visible(request))
        return Response(self.serializer_class(tipos, many=True).data)