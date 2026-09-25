from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.revision_serializer import RevisionSerializer
from apps.investigacion_formativa.services.revision_service import RevisionService
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_CALIFICACION_PROCESO, combinar,
)
from rest_framework.decorators import action


class RevisionViewSet(viewsets.ViewSet):
    """Append-only: no expone update() ni destroy(), igual que RevisionService
    (ver decisión documentada en revision_validator/revision_service)."""

    serializer_class = RevisionSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_CALIFICACION_PROCESO), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_instancia_etapa
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        revisiones = RevisionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(revisiones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        revision = RevisionService.obtener(pk)
        return Response(self.serializer_class(revision).data)

    def create(self, request):
        revision = RevisionService.crear(
            instancia_etapa_id=request.data.get("instancia_etapa"),
            observaciones=request.data.get("observaciones"),
            aprobado=request.data.get("aprobado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(revision).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="por-instancia-etapa/(?P<instancia_etapa_id>[^/.]+)")
    def por_instancia_etapa(self, request, instancia_etapa_id=None):
        revisiones = RevisionService.listar_por_instancia_etapa(instancia_etapa_id)
        return Response(self.serializer_class(revisiones, many=True).data)