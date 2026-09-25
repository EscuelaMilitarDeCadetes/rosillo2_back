from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.investigacion_formal.serializers.tipo_producto_serializer import TipoProductoSerializer
from apps.investigacion_formal.services.tipo_producto_service import TipoProductoService
from apps.investigacion_formal.permissions import ROLES_LECTURA_CATALOGOS, combinar
from apps.usuarios.permissions import EsSoporte


class TipoProductoViewSet(viewsets.ViewSet):
    serializer_class = TipoProductoSerializer
    pagination_class = InvestigacionFormalPageNumberPagination
    
    def get_permissions(self):
        if self.action in ["create", "update"]:
            return [EsSoporte(), TieneAmbitoFormal()]
        else:  # list, retrieve
            return [combinar(ROLES_LECTURA_CATALOGOS), TieneAmbitoFormal()]

    def list(self, request):
        tipos = TipoProductoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tipos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        tipo = TipoProductoService.obtener(pk)
        return Response(self.serializer_class(tipo).data)

    def create(self, request):
        tipo = TipoProductoService.crear(
            tipo_producto=request.data.get("tipo_producto"),
            aplica=request.data.get("aplica"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(tipo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        tipo = TipoProductoService.actualizar(
            tipo_producto_id=pk,
            tipo_producto=request.data.get("tipo_producto"),
            aplica=request.data.get("aplica"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(tipo).data)