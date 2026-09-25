# apps/investigacion_formativa/views/tutor_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.tutor_serializer import TutorSerializer
from apps.investigacion_formativa.services.tutor_service import TutorService
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION, combinar,
)


class TutorViewSet(viewsets.ViewSet):
    serializer_class = TutorSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "activar", "desactivar"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_facultad
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        tutores = TutorService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tutores, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        tutor = TutorService.obtener(pk)
        return Response(self.serializer_class(tutor).data)

    def create(self, request):
        tutor = TutorService.crear(
            persona_id=request.data.get("persona"),
            facultad_id=request.data.get("facultad"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(tutor).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        tutor = TutorService.actualizar(
            tutor_id=pk,
            facultad_id=request.data.get("facultad"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(tutor).data)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        tutor = TutorService.activar(pk, ejecutor=request.user)
        return Response(self.serializer_class(tutor).data)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        tutor = TutorService.desactivar(pk, ejecutor=request.user)
        return Response(self.serializer_class(tutor).data)

    @action(detail=False, methods=["get"], url_path="por-facultad/(?P<facultad_id>[^/.]+)")
    def por_facultad(self, request, facultad_id=None):
        tutores = TutorService.listar_activos_por_facultad(facultad_id)
        return Response(self.serializer_class(tutores, many=True).data)