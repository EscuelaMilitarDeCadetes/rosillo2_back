# apps/investigacion_formativa/views/flujo_proceso_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.flujo_proceso_serializer import FlujoProcesoSerializer
from apps.investigacion_formativa.services.flujo_proceso_service import FlujoProcesoService
from apps.investigacion_formativa.permissions import (
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
)


class FlujoProcesoViewSet(viewsets.ViewSet):

    serializer_class = FlujoProcesoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "activar", "desactivar"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, activos, por_modalidad, vigente
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        flujos = FlujoProcesoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(flujos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        flujo = FlujoProcesoService.obtener(pk)
        return Response(self.serializer_class(flujo).data)

    def create(self, request):
        flujo = FlujoProcesoService.crear(
            modalidad_id=request.data.get("modalidad"),
            nombre=request.data.get("nombre"),
            version=request.data.get("version"),
            tipo=request.data.get("tipo"),
            descripcion=request.data.get("descripcion"),
            fecha_vigencia_inicio=request.data.get("fecha_vigencia_inicio"),
            fecha_vigencia_fin=request.data.get("fecha_vigencia_fin"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(flujo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        flujo = FlujoProcesoService.actualizar(
            flujo_id=pk,
            nombre=request.data.get("nombre"),
            descripcion=request.data.get("descripcion"),
            fecha_vigencia_inicio=request.data.get("fecha_vigencia_inicio"),
            fecha_vigencia_fin=request.data.get("fecha_vigencia_fin"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(flujo).data)

    @action(detail=False, methods=["get"], url_path="activos")
    def activos(self, request):
        activo = request.query_params.get("activo")
        if activo is not None:
            activo = activo.lower() == "true"
        flujos = FlujoProcesoService.listar_activos()
        return Response(self.serializer_class(flujos, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-modalidad/(?P<modalidad_id>[^/.]+)")
    def por_modalidad(self, request, modalidad_id=None):
        activo = request.query_params.get("activo")
        if activo is not None:
            activo = activo.lower() == "true"
        flujos = FlujoProcesoService.listar_por_modalidad(modalidad_id, activo=activo)
        return Response(self.serializer_class(flujos, many=True).data)

    @action(detail=False, methods=["get"], url_path="vigente/(?P<modalidad_id>[^/.]+)")
    def vigente(self, request, modalidad_id=None):
        flujo = FlujoProcesoService.obtener_version_vigente(modalidad_id)
        if flujo is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(self.serializer_class(flujo).data)

    @action(detail=True, methods=["patch"], url_path="activar")
    def activar(self, request, pk=None):
        flujo = FlujoProcesoService.activar(flujo_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(flujo).data)

    @action(detail=True, methods=["patch"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        flujo = FlujoProcesoService.eliminar(flujo_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(flujo).data)