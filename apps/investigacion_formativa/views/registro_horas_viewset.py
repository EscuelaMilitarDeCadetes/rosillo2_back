from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.registro_horas_serializer import (
    RegistroHorasSerializer,
)
from apps.investigacion_formativa.services.registro_horas_service import RegistroHorasService
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION, combinar,
)


class RegistroHorasViewSet(viewsets.ViewSet):
    serializer_class = RegistroHorasSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "ajustar_horas_requeridas", "recalcular"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_proceso
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        controles = RegistroHorasService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(controles, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        control = RegistroHorasService.obtener(pk)
        return Response(self.serializer_class(control).data)

    def create(self, request):
        control = RegistroHorasService.crear(
            proceso_id=request.data.get("proceso"),
            ejecutor=request.user,
            horas_requeridas=request.data.get("horas_requeridas", 120),
        )
        return Response(self.serializer_class(control).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="ajustar-horas-requeridas")
    def ajustar_horas_requeridas(self, request, pk=None):
        control = RegistroHorasService.ajustar_horas_requeridas(
            registro_horas_id=pk,
            nuevas_horas_requeridas=request.data.get("horas_requeridas"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(control).data)

    @action(detail=True, methods=["post"])
    def recalcular(self, request, pk=None):
        control = RegistroHorasService.recalcular(pk, ejecutor=request.user)
        return Response(self.serializer_class(control).data)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        control = RegistroHorasService.obtener_por_proceso(proceso_id)
        if control is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(self.serializer_class(control).data)