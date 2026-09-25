from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.investigacion_formal.serializers.punto_control_serializer import PuntoControlSerializer
from apps.investigacion_formal.services.punto_control_service import PuntoControlService
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_CREACION_OPERATIVA, combinar,
)


class PuntoControlViewSet(viewsets.ViewSet):
    serializer_class = PuntoControlSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_CREACION_OPERATIVA), TieneAmbitoFormal()]
        else:  # list, retrieve
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        puntos = PuntoControlService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(puntos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        punto = PuntoControlService.obtener(pk)
        return Response(self.serializer_class(punto).data)

    def create(self, request):
        punto = PuntoControlService.crear(
            control=request.data.get("control"),
            peso=request.data.get("peso"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(punto).data, status=status.HTTP_201_CREATED)