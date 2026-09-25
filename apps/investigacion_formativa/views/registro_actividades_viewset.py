from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.registro_actividades_serializer import (
    RegistroActividadesSerializer,
)
from apps.investigacion_formativa.services.registro_actividades_service import (
    RegistroActividadesService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_AUTOR_REGISTRO_ACTIVIDADES,
    ROLES_APROBACION_REGISTRO_ACTIVIDADES, combinar,
)


class RegistroActividadesViewSet(viewsets.ViewSet):
    serializer_class = RegistroActividadesSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [combinar(ROLES_AUTOR_REGISTRO_ACTIVIDADES), TieneAmbitoFormativa()]
        elif self.action == "aprobar":
            return [combinar(ROLES_APROBACION_REGISTRO_ACTIVIDADES), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_proceso
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        registros = RegistroActividadesService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        registro = RegistroActividadesService.obtener(pk)
        return Response(self.serializer_class(registro).data)

    def create(self, request):
        registro = RegistroActividadesService.crear(
            proceso_id=request.data.get("proceso"),
            registrado_por_id=request.user.pk,
            tipo_periodo=request.data.get("tipo_periodo"),
            actividades=request.data.get("actividades"),
            ejecutor=request.user,
            horas_reportadas=request.data.get("horas_reportadas", 0),
            fecha_periodo=request.data.get("fecha_periodo"),
            documento_id=request.data.get("documento"),
            nota=request.data.get("nota"),
        )
        return Response(self.serializer_class(registro).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        registro = RegistroActividadesService.actualizar(
            registro_id=pk,
            tipo_periodo=request.data.get("tipo_periodo"),
            actividades=request.data.get("actividades"),
            horas_reportadas=request.data.get("horas_reportadas", 0),
            ejecutor=request.user,
            fecha_periodo=request.data.get("fecha_periodo"),
            documento_id=request.data.get("documento"),
            nota=request.data.get("nota"),
        )
        return Response(self.serializer_class(registro).data)

    def destroy(self, request, pk=None):
        RegistroActividadesService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        registro = RegistroActividadesService.aprobar(pk, ejecutor=request.user)
        return Response(self.serializer_class(registro).data)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        registros = RegistroActividadesService.listar_por_proceso(proceso_id)
        return Response(self.serializer_class(registros, many=True).data)