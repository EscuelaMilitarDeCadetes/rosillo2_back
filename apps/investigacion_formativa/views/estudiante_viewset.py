# apps/investigacion_formativa/views/estudiante_viewset.py

from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.estudiante_serializer import EstudianteSerializer
from apps.investigacion_formativa.services.estudiante_service import EstudianteService
from apps.investigacion_formativa.permissions import (
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
)


class EstudianteViewSet(viewsets.ViewSet):
    serializer_class = EstudianteSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "desactivar", "reactivar"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_facultad, por_modalidad, por_modalidad_facultad
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        estudiantes = EstudianteService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(estudiantes, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        estudiante = EstudianteService.obtener(pk)
        return Response(self.serializer_class(estudiante).data)

    def create(self, request):
        estudiante = EstudianteService.crear(
            persona_id=request.data.get("persona"),
            modalidad_facultad_id=request.data.get("modalidad_facultad"),
            correo_personal=request.data.get("correo_personal"),
            nivel=request.data.get("nivel"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(estudiante).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        estudiante = EstudianteService.actualizar(
            estudiante_id=pk,
            correo_personal=request.data.get("correo_personal"),
            nivel=request.data.get("nivel"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(estudiante).data)

    @action(detail=False, methods=["get"], url_path="por-facultad/(?P<facultad_id>[^/.]+)")
    def por_facultad(self, request, facultad_id=None):
        estado = request.query_params.get("estado")
        if estado is not None:
            estado = estado.lower() == "true"
        estudiantes = EstudianteService.listar_por_facultad(facultad_id, estado=estado)
        return Response(self.serializer_class(estudiantes, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-modalidad/(?P<modalidad_id>[^/.]+)")
    def por_modalidad(self, request, modalidad_id=None):
        estado = request.query_params.get("estado")
        if estado is not None:
            estado = estado.lower() == "true"
        estudiantes = EstudianteService.listar_por_modalidad(modalidad_id, estado=estado)
        return Response(self.serializer_class(estudiantes, many=True).data)

    @action(detail=True, methods=["patch"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        estudiante = EstudianteService.eliminar(estudiante_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(estudiante).data)

    @action(detail=True, methods=["patch"], url_path="reactivar")
    def reactivar(self, request, pk=None):
        estudiante = EstudianteService.activar(estudiante_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(estudiante).data)
    
    @action(detail=False, methods=["get"], url_path="por-modalidad-facultad/(?P<modalidad_facultad_id>[^/.]+)")
    def por_modalidad_facultad(self, request, modalidad_facultad_id=None):
        estado = request.query_params.get("estado")
        if estado is not None:
            estado = estado.lower() == "true"
        estudiantes = EstudianteService.listar_por_modalidad_facultad(modalidad_facultad_id, estado=estado)
        return Response(self.serializer_class(estudiantes, many=True).data)