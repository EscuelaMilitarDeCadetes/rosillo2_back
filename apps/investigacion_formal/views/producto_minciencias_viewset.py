from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formal.serializers.producto_minciencias_serializer import (
    ProductoMincienciasSerializer,
)
from apps.investigacion_formal.services.producto_minciencias_service import (
    ProductoMincienciasService,
)
from apps.investigacion_formal.permissions import ROLES_LECTURA_CATALOGOS, combinar
from apps.usuarios.permissions import EsSoporte


class ProductoMincienciasViewSet(viewsets.ViewSet):
    serializer_class = ProductoMincienciasSerializer
    pagination_class = InvestigacionFormalPageNumberPagination
    
    def get_permissions(self):
        if self.action in ["create", "update"]:
            return [EsSoporte(), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto
            return [combinar(ROLES_LECTURA_CATALOGOS), TieneAmbitoFormal()]

    def list(self, request):
        productos = ProductoMincienciasService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(productos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        producto = ProductoMincienciasService.obtener(pk)
        return Response(self.serializer_class(producto).data)

    def create(self, request):
        producto = ProductoMincienciasService.crear(
            nombre_producto=request.data.get("nombre_producto"),
            nomenclatura=request.data.get("nomenclatura"),
            peso=request.data.get("peso"),
            vigencia=request.data.get("vigencia"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(producto).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        producto = ProductoMincienciasService.actualizar(
            producto_minciencias_id=pk,
            nombre_producto=request.data.get("nombre_producto"),
            nomenclatura=request.data.get("nomenclatura"),
            peso=request.data.get("peso"),
            vigencia=request.data.get("vigencia"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(producto).data)