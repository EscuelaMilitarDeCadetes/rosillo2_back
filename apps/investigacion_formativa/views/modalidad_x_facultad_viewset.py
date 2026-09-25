# apps/investigacion_formativa/views/modalidad_x_facultad_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.modalidad_x_facultad_serializer import (
    ModalidadXFacultadSerializer,
)
from apps.investigacion_formativa.services.modalidad_x_facultad_service import (
    ModalidadXFacultadService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION, combinar,
)


class ModalidadXFacultadViewSet(viewsets.ViewSet):
    serializer_class = ModalidadXFacultadSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "habilitar", "deshabilitar"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_facultad
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        vinculos = ModalidadXFacultadService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(vinculos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vinculo = ModalidadXFacultadService.obtener(pk)
        return Response(self.serializer_class(vinculo).data)

    def create(self, request):
        vinculo = ModalidadXFacultadService.crear(
            facultad_id=request.data.get("facultad"),
            modalidad_id=request.data.get("modalidad"),
            ejecutor=request.user,
            disponible=request.data.get("disponible", True),
        )
        return Response(self.serializer_class(vinculo).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def habilitar(self, request, pk=None):
        vinculo = ModalidadXFacultadService.habilitar(pk, ejecutor=request.user)
        return Response(self.serializer_class(vinculo).data)

    @action(detail=True, methods=["post"])
    def deshabilitar(self, request, pk=None):
        vinculo = ModalidadXFacultadService.deshabilitar(pk, ejecutor=request.user)
        return Response(self.serializer_class(vinculo).data)

    @action(detail=False, methods=["get"], url_path="por-facultad/(?P<facultad_id>[^/.]+)")
    def por_facultad(self, request, facultad_id=None):
        disponible_raw = request.query_params.get("disponible")
        disponible = None
        if disponible_raw is not None:
            disponible = disponible_raw.lower() in ("true", "1")
        vinculos = ModalidadXFacultadService.listar_por_facultad(facultad_id, disponible=disponible)
        return Response(self.serializer_class(vinculos, many=True).data)