# apps/investigacion_formativa/views/evento_evaluativo_viewset.py

from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.evento_evaluativo_serializer import EventoEvaluativoSerializer
from apps.investigacion_formativa.services.evento_evaluativo_service import EventoEvaluativoService
from apps.investigacion_formativa.permissions import (
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
)


class EventoEvaluativoViewSet(viewsets.ViewSet):
    serializer_class = EventoEvaluativoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "reprogramar", "registrar_resultado", "cargar_acta", "destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_proceso, proximas
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        eventos = EventoEvaluativoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(eventos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        evento = EventoEvaluativoService.obtener(pk)
        return Response(self.serializer_class(evento).data)

    def create(self, request):
        evento = EventoEvaluativoService.crear(
            proceso_formativo_id=request.data.get("proceso_formativo"),
            numero=request.data.get("numero"),
            es_obligatoria=request.data.get("es_obligatoria", True),
            fecha_sustentacion=request.data.get("fecha_sustentacion"),
            lugar=request.data.get("lugar"),
            ejecutor=request.user,
            usuario_revisor_id=request.data.get("usuario_revisor"),
        )
        return Response(self.serializer_class(evento).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        EventoEvaluativoService.eliminar(evento_id=pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        eventos = EventoEvaluativoService.listar_por_proceso(proceso_id)
        return Response(self.serializer_class(eventos, many=True).data)

    @action(detail=False, methods=["get"], url_path="proximas")
    def proximas(self, request):
        proceso_id = request.query_params.get("proceso")
        eventos = EventoEvaluativoService.listar_proximas(proceso_formativo_id=proceso_id)
        return Response(self.serializer_class(eventos, many=True).data)

    @action(detail=True, methods=["patch"], url_path="reprogramar")
    def reprogramar(self, request, pk=None):
        evento = EventoEvaluativoService.reprogramar(
            evento_id=pk,
            fecha_sustentacion=request.data.get("fecha_sustentacion"),
            lugar=request.data.get("lugar"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(evento).data)

    @action(detail=True, methods=["patch"], url_path="registrar-resultado")
    def registrar_resultado(self, request, pk=None):
        evento = EventoEvaluativoService.registrar_resultado(
            evento_id=pk,
            resultado=request.data.get("resultado"),
            acta_sustentacion_id=request.data.get("acta_sustentacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(evento).data)

    @action(detail=True, methods=["patch"], url_path="cargar-acta")
    def cargar_acta(self, request, pk=None):
        evento = EventoEvaluativoService.cargar_acta(
            evento_id=pk,
            acta_sustentacion_id=request.data.get("acta_sustentacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(evento).data)