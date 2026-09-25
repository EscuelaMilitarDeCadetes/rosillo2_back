from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.investigacion_formal.serializers.grupo_minciencias_serializer import (
    GrupoMincienciasSerializer,
)
from apps.investigacion_formal.services.grupo_minciencias_service import GrupoMincienciasService
from apps.investigacion_formal.permissions import ROLES_LECTURA_CATALOGOS, combinar
from apps.usuarios.permissions import EsSoporte, TieneAmbitoFormal


class GrupoMincienciasViewSet(viewsets.ViewSet):
    serializer_class = GrupoMincienciasSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update"]:
            return [EsSoporte(), TieneAmbitoFormal()]
        else:  # list, retrieve
            return [combinar(ROLES_LECTURA_CATALOGOS), TieneAmbitoFormal()]

    def list(self, request):
        grupos = GrupoMincienciasService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(grupos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        grupo = GrupoMincienciasService.obtener(pk)
        return Response(self.serializer_class(grupo).data)

    def create(self, request):
        grupo = GrupoMincienciasService.crear(
            nombre_grupo_minciencias=request.data.get("nombre_grupo_minciencias"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(grupo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        grupo = GrupoMincienciasService.actualizar(
            grupo_minciencias_id=pk,
            nombre_grupo_minciencias=request.data.get("nombre_grupo_minciencias"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(grupo).data)