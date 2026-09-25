from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.crm.serializers import InteraccionSerializer
from apps.crm.services.interaccion_service import InteraccionService
from apps.crm.pagination import CrmPageNumberPagination
from apps.usuarios.permissions import *


class InteraccionViewSet(viewsets.ViewSet):
    serializer_class = InteraccionSerializer
    pagination_class = CrmPageNumberPagination

    def get_permissions(self):
        permission_classes = [EsSoporte | EsCInterno | EsCExterno | EsFacultad]
        return [permission() for permission in permission_classes]

    def list(self, request):
        interacciones = InteraccionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(interacciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        interaccion = InteraccionService.obtener(pk)
        serializer = self.serializer_class(interaccion)
        return Response(serializer.data)

    def create(self, request):
        interaccion = InteraccionService.crear(
            entidad_id=request.data.get("entidad"),
            medio=request.data.get("medio"),
            resumen=request.data.get("resumen"),
            proyecto_asociado_id=request.data.get("proyecto_asociado"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(interaccion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        interaccion = InteraccionService.actualizar(
            interaccion_id=pk,
            ejecutor=request.user,
            entidad_id=request.data.get("entidad"),
            medio=request.data.get("medio"),
            resumen=request.data.get("resumen"),
            proyecto_asociado_id=request.data.get("proyecto_asociado"),
        )
        serializer = self.serializer_class(interaccion)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        interaccion = InteraccionService.actualizar(
            interaccion_id=pk,
            ejecutor=request.user,
            entidad_id=request.data.get("entidad"),
            medio=request.data.get("medio"),
            resumen=request.data.get("resumen"),
            proyecto_asociado_id=request.data.get("proyecto_asociado"),
        )
        serializer = self.serializer_class(interaccion)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        InteraccionService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-entidad/(?P<entidad_id>[^/.]+)")
    def por_entidad(self, request, entidad_id=None):
        interacciones = InteraccionService.listar_por_entidad(entidad_id)
        serializer = self.serializer_class(interacciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        interacciones = InteraccionService.listar_por_proyecto(proyecto_id)
        serializer = self.serializer_class(interacciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-medio")
    def por_medio(self, request):
        medio = request.query_params.get("medio")
        interacciones = InteraccionService.listar_por_medio(medio)
        serializer = self.serializer_class(interacciones, many=True)
        return Response(serializer.data)