from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_ESCRITURA_GESTION, ROLES_CREACION_OPERATIVA, ProyectoTieneActaInicio, combinar,
)
from apps.investigacion_formal.serializers.objetivos_serializer import ObjetivosSerializer
from apps.investigacion_formal.services.objetivos_service import ObjetivosService


class ObjetivosViewSet(viewsets.ViewSet):
    serializer_class = ObjetivosSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "crear_objetivo_general", "crear_objetivo_especifico"]:
            return [combinar(ROLES_CREACION_OPERATIVA), TieneAmbitoFormal(), ProyectoTieneActaInicio()]
        elif self.action in ["update", "destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto, objetivo_general
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        objetivos = ObjetivosService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(objetivos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        objetivo = ObjetivosService.obtener(pk)
        return Response(self.serializer_class(objetivo).data)

    @action(detail=False, methods=["post"], url_path="objetivo-general")
    def crear_objetivo_general(self, request):
        objetivo = ObjetivosService.crear_objetivo_general(
            proyecto_id=request.data.get("proyecto"),
            objetivo=request.data.get("objetivo"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(objetivo).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="objetivo-especifico")
    def crear_objetivo_especifico(self, request):
        objetivo = ObjetivosService.crear_objetivo_especifico(
            proyecto_id=request.data.get("proyecto"),
            objetivo=request.data.get("objetivo"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(objetivo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        objetivo = ObjetivosService.actualizar(
            objetivo_id=pk,
            objetivo=request.data.get("objetivo"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(objetivo).data)

    def destroy(self, request, pk=None):
        ObjetivosService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        solo_activos = request.query_params.get("solo_activos", "true").lower() != "false"
        objetivos = ObjetivosService.listar_por_proyecto(proyecto_id, solo_activos=solo_activos)
        return Response(self.serializer_class(objetivos, many=True).data)

    @action(detail=False, methods=["get"], url_path="objetivo-general/(?P<proyecto_id>[^/.]+)")
    def objetivo_general(self, request, proyecto_id=None):
        objetivo = ObjetivosService.obtener_objetivo_general(proyecto_id)
        if objetivo is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.serializer_class(objetivo).data)