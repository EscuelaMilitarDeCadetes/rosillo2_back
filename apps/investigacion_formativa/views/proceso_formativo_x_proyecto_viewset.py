from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.proceso_formativo_x_proyecto_serializer import (
    ProcesoFormativoXProyectoSerializer,
)
from apps.investigacion_formativa.services.proceso_formativo_x_proyecto_service import (
    ProcesoFormativoXProyectoService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION, combinar,
)


class ProcesoFormativoXProyectoViewSet(viewsets.ViewSet):
    serializer_class = ProcesoFormativoXProyectoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_proceso_formativo
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        vinculos = ProcesoFormativoXProyectoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(vinculos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vinculo = ProcesoFormativoXProyectoService.obtener(pk)
        return Response(self.serializer_class(vinculo).data)

    def create(self, request):
        vinculo = ProcesoFormativoXProyectoService.crear(
            proceso_formativo_id=request.data.get("proceso_formativo"),
            proyecto_formal_id=request.data.get("proyecto_formal"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(vinculo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        vinculo = ProcesoFormativoXProyectoService.actualizar(
            vinculo_id=pk,
            proceso_formativo_id=request.data.get("proceso_formativo"),
            proyecto_formal_id=request.data.get("proyecto_formal"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(vinculo).data)

    def destroy(self, request, pk=None):
        ProcesoFormativoXProyectoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-proceso-formativo/(?P<proceso_formativo_id>[^/.]+)")
    def por_proceso_formativo(self, request, proceso_formativo_id=None):
        vinculos = ProcesoFormativoXProyectoService.listar_por_proceso_formativo(proceso_formativo_id)
        return Response(self.serializer_class(vinculos, many=True).data)