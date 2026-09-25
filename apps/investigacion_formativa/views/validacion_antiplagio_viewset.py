# apps/investigacion_formativa/views/validacion_antiplagio_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.validacion_antiplagio_serializer import (
    ValidacionAntiplagioSerializer,
)
from apps.investigacion_formativa.services.validacion_antiplagio_service import (
    ValidacionAntiplagioService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION, combinar,
)


class ValidacionAntiplagioViewSet(viewsets.ViewSet):
    serializer_class = ValidacionAntiplagioSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_instancia_etapa
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        validaciones = ValidacionAntiplagioService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(validaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        validacion = ValidacionAntiplagioService.obtener(pk)
        return Response(self.serializer_class(validacion).data)

    def create(self, request):
        validacion = ValidacionAntiplagioService.crear(
            instancia_etapa_id=request.data.get("instancia_etapa"),
            documento_id=request.data.get("documento"),
            porcentaje=request.data.get("porcentaje"),
            aprobado=request.data.get("aprobado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(validacion).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        validacion = ValidacionAntiplagioService.actualizar(
            validacion_id=pk,
            porcentaje=request.data.get("porcentaje"),
            aprobado=request.data.get("aprobado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(validacion).data)

    @action(detail=False, methods=["get"], url_path="por-instancia-etapa/(?P<instancia_etapa_id>[^/.]+)")
    def por_instancia_etapa(self, request, instancia_etapa_id=None):
        validaciones = ValidacionAntiplagioService.listar_por_instancia_etapa(instancia_etapa_id)
        return Response(self.serializer_class(validaciones, many=True).data)