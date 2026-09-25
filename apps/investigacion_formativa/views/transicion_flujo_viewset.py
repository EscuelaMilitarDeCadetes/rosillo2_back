# apps/investigacion_formativa/views/transicion_flujo_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.transicion_flujo_serializer import (
    TransicionFlujoSerializer,
)
from apps.investigacion_formativa.services.transicion_flujo_service import (
    TransicionFlujoService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_CONFIGURACION_FLUJO, combinar,
)


class TransicionFlujoViewSet(viewsets.ViewSet):
    serializer_class = TransicionFlujoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "activar", "desactivar"]:
            return [combinar(ROLES_CONFIGURACION_FLUJO), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_etapa_origen
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        transiciones = TransicionFlujoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(transiciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        transicion = TransicionFlujoService.obtener(pk)
        return Response(self.serializer_class(transicion).data)

    def create(self, request):
        transicion = TransicionFlujoService.crear(
            etapa_origen_id=request.data.get("etapa_origen"),
            etapa_destino_id=request.data.get("etapa_destino"),
            nombre=request.data.get("nombre"),
            ejecutor=request.user,
            condicion=request.data.get("condicion"),
            accion_automatica=request.data.get("accion_automatica"),
            orden=request.data.get("orden", 0),
        )
        return Response(self.serializer_class(transicion).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        transicion = TransicionFlujoService.actualizar(
            transicion_id=pk,
            etapa_origen_id=request.data.get("etapa_origen"),
            etapa_destino_id=request.data.get("etapa_destino"),
            nombre=request.data.get("nombre"),
            ejecutor=request.user,
            condicion=request.data.get("condicion"),
            accion_automatica=request.data.get("accion_automatica"),
            orden=request.data.get("orden", 0),
        )
        return Response(self.serializer_class(transicion).data)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        transicion = TransicionFlujoService.activar(pk, ejecutor=request.user)
        return Response(self.serializer_class(transicion).data)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        transicion = TransicionFlujoService.desactivar(pk, ejecutor=request.user)
        return Response(self.serializer_class(transicion).data)

    @action(detail=False, methods=["get"], url_path="por-etapa-origen/(?P<etapa_origen_id>[^/.]+)")
    def por_etapa_origen(self, request, etapa_origen_id=None):
        transiciones = TransicionFlujoService.listar_por_etapa_origen(etapa_origen_id)
        return Response(self.serializer_class(transiciones, many=True).data)