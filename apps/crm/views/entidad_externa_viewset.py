from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.crm.serializers import EntidadExternaSerializer
from apps.crm.services.entidad_externa_service import EntidadExternaService
from apps.crm.pagination import CrmPageNumberPagination
from apps.usuarios.permissions import *


class EntidadExternaViewSet(viewsets.ViewSet):
    serializer_class = EntidadExternaSerializer
    pagination_class = CrmPageNumberPagination

    def get_permissions(self):
        permission_classes = [EsSoporte | EsCInterno | EsCExterno | EsFacultad]
        return [permission() for permission in permission_classes]

    def list(self, request):
        entidades = EntidadExternaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(entidades, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        entidad = EntidadExternaService.obtener(pk)
        serializer = self.serializer_class(entidad)
        return Response(serializer.data)

    def create(self, request):
        entidad = EntidadExternaService.crear(
            nombre=request.data.get("nombre"),
            sector=request.data.get("sector"),
            pais=request.data.get("pais"),
            tipo_relacion=request.data.get("tipo_relacion"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(entidad)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        entidad = EntidadExternaService.actualizar(
            entidad_id=pk,
            ejecutor=request.user,
            nombre=request.data.get("nombre"),
            sector=request.data.get("sector"),
            pais=request.data.get("pais"),
            tipo_relacion=request.data.get("tipo_relacion"),
        )
        serializer = self.serializer_class(entidad)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        entidad = EntidadExternaService.actualizar(
            entidad_id=pk,
            ejecutor=request.user,
            nombre=request.data.get("nombre"),
            sector=request.data.get("sector"),
            pais=request.data.get("pais"),
            tipo_relacion=request.data.get("tipo_relacion"),
        )
        serializer = self.serializer_class(entidad)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        EntidadExternaService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-tipo-relacion")
    def por_tipo_relacion(self, request):
        tipo_relacion = request.query_params.get("tipo_relacion")
        entidades = EntidadExternaService.listar_por_tipo_relacion(tipo_relacion)
        serializer = self.serializer_class(entidades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-sector")
    def por_sector(self, request):
        sector = request.query_params.get("sector")
        entidades = EntidadExternaService.listar_por_sector(sector)
        serializer = self.serializer_class(entidades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-pais")
    def por_pais(self, request):
        pais = request.query_params.get("pais")
        entidades = EntidadExternaService.listar_por_pais(pais)
        serializer = self.serializer_class(entidades, many=True)
        return Response(serializer.data)