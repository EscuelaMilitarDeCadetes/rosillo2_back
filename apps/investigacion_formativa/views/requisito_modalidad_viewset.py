from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.requisito_modalidad_serializer import (
    RequisitoModalidadSerializer,
)
from apps.investigacion_formativa.services.requisito_modalidad_service import (
    RequisitoModalidadService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION, combinar,
)


class RequisitoModalidadViewSet(viewsets.ViewSet):
    serializer_class = RequisitoModalidadSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_modalidad
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        requisitos = RequisitoModalidadService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(requisitos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        requisito = RequisitoModalidadService.obtener(pk)
        return Response(self.serializer_class(requisito).data)

    def create(self, request):
        requisito = RequisitoModalidadService.crear(
            modalidad_id=request.data.get("modalidad"),
            tipo=request.data.get("tipo"),
            descripcion=request.data.get("descripcion"),
            ejecutor=request.user,
            valor_numerico=request.data.get("valor_numerico"),
            valor_booleano=request.data.get("valor_booleano"),
        )
        return Response(self.serializer_class(requisito).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        requisito = RequisitoModalidadService.actualizar(
            requisito_id=pk,
            tipo=request.data.get("tipo"),
            descripcion=request.data.get("descripcion"),
            ejecutor=request.user,
            valor_numerico=request.data.get("valor_numerico"),
            valor_booleano=request.data.get("valor_booleano"),
        )
        return Response(self.serializer_class(requisito).data)

    def destroy(self, request, pk=None):
        RequisitoModalidadService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-modalidad/(?P<modalidad_id>[^/.]+)")
    def por_modalidad(self, request, modalidad_id=None):
        requisitos = RequisitoModalidadService.listar_activos_por_modalidad(modalidad_id)
        return Response(self.serializer_class(requisitos, many=True).data)