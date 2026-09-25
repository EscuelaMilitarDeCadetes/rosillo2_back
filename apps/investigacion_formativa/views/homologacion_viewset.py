# apps/investigacion_formativa/views/homologacion_viewset.py

from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.homologacion_serializer import HomologacionSerializer
from apps.investigacion_formativa.services.homologacion_service import HomologacionService
from apps.investigacion_formativa.permissions import (
    ROLES_AUTOR_HOMOLOGACION,
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
)


class HomologacionViewSet(viewsets.ViewSet):
    serializer_class = HomologacionSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_AUTOR_HOMOLOGACION), TieneAmbitoFormativa()]
        if self.action in ["aprobar", "rechazar", "cargar_acta"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def create(self, request):
        homologacion = HomologacionService.crear(
            proceso_id=request.data.get("proceso"),
            ejecutor=request.user,
            observaciones=request.data.get("observaciones"),
        )
        return Response(self.serializer_class(homologacion).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        homologaciones = HomologacionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(homologaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        homologacion = HomologacionService.obtener(pk)
        return Response(self.serializer_class(homologacion).data)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        homologacion = HomologacionService.obtener_por_proceso(proceso_id)
        if homologacion is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(self.serializer_class(homologacion).data)

    @action(detail=False, methods=["get"], url_path="pendientes")
    def pendientes(self, request):
        homologaciones = HomologacionService.listar_pendientes()
        return Response(self.serializer_class(homologaciones, many=True).data)

    @action(detail=True, methods=["patch"], url_path="aprobar")
    def aprobar(self, request, pk=None):
        homologacion = HomologacionService.aprobar(
            homologacion_id=pk,
            aprobado_por_id=request.user.id,
            creditos_reconocidos=request.data.get("creditos_reconocidos"),
            acta_homologacion_id=request.data.get("acta_homologacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(homologacion).data)

    @action(detail=True, methods=["patch"], url_path="rechazar")
    def rechazar(self, request, pk=None):
        homologacion = HomologacionService.rechazar(
            homologacion_id=pk,
            observaciones=request.data.get("observaciones"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(homologacion).data)

    @action(detail=True, methods=["patch"], url_path="cargar-acta")
    def cargar_acta(self, request, pk=None):
        homologacion = HomologacionService.cargar_acta(
            homologacion_id=pk,
            acta_homologacion_id=request.data.get("acta_homologacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(homologacion).data)