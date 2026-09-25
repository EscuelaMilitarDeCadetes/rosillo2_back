from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formal.serializers.producto_x_grupo_serializer import (
    ProductoXGrupoSerializer,
)
from apps.investigacion_formal.services.producto_x_grupo_service import ProductoXGrupoService
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_ESCRITURA_GESTION, ROLES_CREACION_OPERATIVA, combinar,
)
from apps.usuarios.permissions import EsSoporte


class ProductoXGrupoViewSet(viewsets.ViewSet):
    serializer_class = ProductoXGrupoSerializer
    pagination_class = InvestigacionFormalPageNumberPagination
    
    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_CREACION_OPERATIVA + [EsSoporte]), TieneAmbitoFormal()]
        elif self.action in ["update", "destroy", "registrar_entrega", "subir_a_gruplac"]:
            return [combinar(ROLES_ESCRITURA_GESTION + [EsSoporte]), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto, pendientes, entregados
            return [combinar(ROLES_LECTURA_CATALOGOS + [EsSoporte]), TieneAmbitoFormal()]

    def list(self, request):
        registros = ProductoXGrupoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        registro = ProductoXGrupoService.obtener(pk)
        return Response(self.serializer_class(registro).data)

    def create(self, request):
        registro = ProductoXGrupoService.crear(
            producto_minciencias_id=request.data.get("producto_minciencias"),
            grupo_minciencias_id=request.data.get("grupo_minciencias"),
            tipo_producto_id=request.data.get("tipo_producto"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(registro).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        registro = ProductoXGrupoService.actualizar(
            producto_x_grupo_id=pk,
            producto_minciencias_id=request.data.get("producto_minciencias"),
            grupo_minciencias_id=request.data.get("grupo_minciencias"),
            tipo_producto_id=request.data.get("tipo_producto"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(registro).data)

    @action(detail=False, methods=["get"], url_path="por-producto-minciencias/(?P<producto_minciencias_id>[^/.]+)")
    def por_producto_minciencias(self, request, producto_minciencias_id=None):
        registro = ProductoXGrupoService.obtener_por_producto_minciencias(producto_minciencias_id)
        if registro is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.serializer_class(registro).data)

    @action(detail=False, methods=["get"], url_path="por-grupo-minciencias/(?P<grupo_minciencias_id>[^/.]+)")
    def por_grupo_minciencias(self, request, grupo_minciencias_id=None):
        registros = ProductoXGrupoService.listar_por_grupo_minciencias(grupo_minciencias_id)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-tipo-producto/(?P<tipo_producto_id>[^/.]+)")
    def por_tipo_producto(self, request, tipo_producto_id=None):
        registros = ProductoXGrupoService.listar_por_tipo_producto(tipo_producto_id)
        return Response(self.serializer_class(registros, many=True).data)