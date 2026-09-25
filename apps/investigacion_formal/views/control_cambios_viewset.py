from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formal.serializers.control_cambios_serializer import (
    ControlCambiosSerializer,
)
from apps.investigacion_formal.services.control_cambios_service import ControlCambiosService
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_CREACION_OPERATIVA, combinar,
)
from apps.usuarios.permissions import EsCInterno, EsCExterno, TieneAmbitoFormal


class ControlCambiosViewSet(viewsets.ViewSet):
    serializer_class = ControlCambiosSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action in ["create"]:
            return [combinar(ROLES_CREACION_OPERATIVA), TieneAmbitoFormal()]
        elif self.action in ["actualizar_banderas"]:
            permission_classes = [EsCInterno | EsCExterno]
            return [permission() for permission in permission_classes] + [TieneAmbitoFormal()]
        else:
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        registros = ControlCambiosService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        registro = ControlCambiosService.obtener(pk)
        return Response(self.serializer_class(registro).data)

    def create(self, request):
        registro = ControlCambiosService.crear(
            proyecto_id=request.data.get("proyecto"),
            tipo_cambio=request.data.get("tipo_cambio"),
            ejecutor=request.user,
            cambio_tiempo=request.data.get("cambio_tiempo", False),
            cambio_investigador=request.data.get("cambio_investigador", False),
            cambio_costo=request.data.get("cambio_costo", False),
            cambio_producto=request.data.get("cambio_producto", False),
            fecha_cambio=request.data.get("fecha_cambio"),
        )
        return Response(self.serializer_class(registro).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="banderas")
    def actualizar_banderas(self, request, pk=None):
        registro = ControlCambiosService.actualizar_banderas(
            control_cambios_id=pk,
            ejecutor=request.user,
            cambio_tiempo=request.data.get("cambio_tiempo"),
            cambio_investigador=request.data.get("cambio_investigador"),
            cambio_costo=request.data.get("cambio_costo"),
            cambio_producto=request.data.get("cambio_producto"),
        )
        return Response(self.serializer_class(registro).data)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        registros = ControlCambiosService.listar_por_proyecto(proyecto_id)
        return Response(self.serializer_class(registros, many=True).data)