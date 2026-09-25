# apps/investigacion_formativa/views/actividad_formativa_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.actividad_formativa_serializer import ActividadFormativaSerializer
from apps.investigacion_formativa.services.actividad_formativa_service import ActividadFormativaService
from apps.investigacion_formativa.permissions import (
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_GESTION_ACTIVIDAD_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
)


class ActividadFormativaViewSet(viewsets.ViewSet):
    serializer_class = ActividadFormativaSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "iniciar", "completar", "cancelar"]:
            # El propio estudiante reporta/completa/cancela su actividad, o
            # Facultad/Decano/Soporte la gestionan en su nombre.
            return [combinar(ROLES_GESTION_ACTIVIDAD_FORMATIVA), TieneAmbitoFormativa()]
        elif self.action == "destroy":
            # Eliminar sigue siendo una accion administrativa.
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_proceso, por_responsable
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        actividades = ActividadFormativaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(actividades, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        actividad = ActividadFormativaService.obtener(pk)
        return Response(self.serializer_class(actividad).data)

    def create(self, request):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=request.data.get("proceso_formativo"),
            responsable_id=request.data.get("responsable"),
            nombre=request.data.get("nombre"),
            descripcion=request.data.get("descripcion"),
            fecha_inicio=request.data.get("fecha_inicio"),
            fecha_fin=request.data.get("fecha_fin"),
            horas_dedicadas=request.data.get("horas_dedicadas"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(actividad).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        actividad = ActividadFormativaService.actualizar(
            actividad_id=pk,
            nombre=request.data.get("nombre"),
            descripcion=request.data.get("descripcion"),
            fecha_inicio=request.data.get("fecha_inicio"),
            fecha_fin=request.data.get("fecha_fin"),
            horas_dedicadas=request.data.get("horas_dedicadas"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(actividad).data)

    def destroy(self, request, pk=None):
        ActividadFormativaService.eliminar(actividad_id=pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        actividades = ActividadFormativaService.listar_por_proceso(proceso_id)
        return Response(self.serializer_class(actividades, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-responsable/(?P<responsable_id>[^/.]+)")
    def por_responsable(self, request, responsable_id=None):
        actividades = ActividadFormativaService.listar_por_responsable(responsable_id)
        return Response(self.serializer_class(actividades, many=True).data)

    @action(detail=True, methods=["patch"], url_path="iniciar")
    def iniciar(self, request, pk=None):
        actividad = ActividadFormativaService.iniciar(actividad_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(actividad).data)

    @action(detail=True, methods=["patch"], url_path="completar")
    def completar(self, request, pk=None):
        actividad = ActividadFormativaService.completar(
            actividad_id=pk,
            documento_soporte_id=request.data.get("documento_soporte"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(actividad).data)

    @action(detail=True, methods=["patch"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        actividad = ActividadFormativaService.cancelar(actividad_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(actividad).data)