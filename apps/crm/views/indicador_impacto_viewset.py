from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.crm.serializers import IndicadorImpactoSerializer
from apps.crm.services.indicador_impacto_service import IndicadorImpactoService
from apps.crm.pagination import CrmPageNumberPagination
from apps.usuarios.permissions import *


class IndicadorImpactoViewSet(viewsets.ViewSet):
    serializer_class = IndicadorImpactoSerializer
    pagination_class = CrmPageNumberPagination

    def get_permissions(self):
        permission_classes = [EsSoporte | EsCInterno | EsCExterno | EsFacultad]
        return [permission() for permission in permission_classes]

    def list(self, request):
        indicadores = IndicadorImpactoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(indicadores, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        indicador = IndicadorImpactoService.obtener(pk)
        serializer = self.serializer_class(indicador)
        return Response(serializer.data)

    def create(self, request):
        indicador = IndicadorImpactoService.crear(
            proyecto_id=request.data.get("proyecto"),
            kpi_nombre=request.data.get("kpi_nombre"),
            valor_proyectado=request.data.get("valor_proyectado"),
            valor_real=request.data.get("valor_real"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(indicador)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        indicador = IndicadorImpactoService.actualizar(
            indicador_id=pk,
            ejecutor=request.user,
            proyecto_id=request.data.get("proyecto"),
            kpi_nombre=request.data.get("kpi_nombre"),
            valor_proyectado=request.data.get("valor_proyectado"),
            valor_real=request.data.get("valor_real"),
        )
        serializer = self.serializer_class(indicador)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        indicador = IndicadorImpactoService.actualizar(
            indicador_id=pk,
            ejecutor=request.user,
            proyecto_id=request.data.get("proyecto"),
            kpi_nombre=request.data.get("kpi_nombre"),
            valor_proyectado=request.data.get("valor_proyectado"),
            valor_real=request.data.get("valor_real"),
        )
        serializer = self.serializer_class(indicador)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        IndicadorImpactoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="actualizar-valor-real")
    def actualizar_valor_real(self, request, pk=None):
        indicador = IndicadorImpactoService.actualizar_valor_real(
            indicador_id=pk,
            nuevo_valor_real=request.data.get("valor_real"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(indicador)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        indicadores = IndicadorImpactoService.listar_por_proyecto(proyecto_id)
        serializer = self.serializer_class(indicadores, many=True)
        return Response(serializer.data)