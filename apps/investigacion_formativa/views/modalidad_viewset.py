from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.modalidad_serializer import ModalidadSerializer
from apps.investigacion_formativa.services.modalidad_service import ModalidadService
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION, combinar,
)


class ModalidadViewSet(viewsets.ViewSet):
    serializer_class = ModalidadSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "activar", "destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, activas
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        modalidades = ModalidadService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(modalidades, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        modalidad = ModalidadService.obtener(pk)
        return Response(self.serializer_class(modalidad).data)

    def create(self, request):
        modalidad = ModalidadService.crear(
            nombre=request.data.get("nombre"),
            codigo=request.data.get("codigo"),
            ejecutor=request.user,
            descripcion=request.data.get("descripcion"),
            requiere_evaluadores=request.data.get("requiere_evaluadores", False),
            requiere_tutor=request.data.get("requiere_tutor"),
            requiere_antiplagio=request.data.get("requiere_antiplagio"),
            requiere_sustentacion=request.data.get("requiere_sustentacion"),
            cantidad_maxima_estudiantes=request.data.get("cantidad_maxima_estudiantes"),
            cantidad_minima_evaluadores=request.data.get("cantidad_minima_evaluadores"),
            permite_homologacion=request.data.get("permite_homologacion"),
            requiere_producto_final=request.data.get("requiere_producto_final"),
        )
        return Response(self.serializer_class(modalidad).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        modalidad = ModalidadService.actualizar(
            modalidad_id=pk,
            nombre=request.data.get("nombre"),
            codigo=request.data.get("codigo"),
            ejecutor=request.user,
            descripcion=request.data.get("descripcion"),
            requiere_evaluadores=request.data.get("requiere_evaluadores", False),
            requiere_tutor=request.data.get("requiere_tutor"),
            requiere_antiplagio=request.data.get("requiere_antiplagio"),
            requiere_sustentacion=request.data.get("requiere_sustentacion"),
            cantidad_maxima_estudiantes=request.data.get("cantidad_maxima_estudiantes"),
            cantidad_minima_evaluadores=request.data.get("cantidad_minima_evaluadores"),
            permite_homologacion=request.data.get("permite_homologacion"),
            requiere_producto_final=request.data.get("requiere_producto_final"),
        )
        return Response(self.serializer_class(modalidad).data)

    def destroy(self, request, pk=None):
        ModalidadService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        modalidad = ModalidadService.activar(pk, ejecutor=request.user)
        return Response(self.serializer_class(modalidad).data)

    @action(detail=False, methods=["get"])
    def activas(self, request):
        modalidades = ModalidadService.listar_activas()
        return Response(self.serializer_class(modalidades, many=True).data)