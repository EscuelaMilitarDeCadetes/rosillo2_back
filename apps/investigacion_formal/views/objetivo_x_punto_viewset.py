from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formal.serializers.objetivo_x_punto_serializer import (
    ObjetivoXPuntoSerializer,
)
from apps.investigacion_formal.services.objetivo_x_punto_service import ObjetivoXPuntoService
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_ESCRITURA_GESTION, ROLES_CREACION_OPERATIVA, ProyectoTieneActaInicio, combinar,
)
from apps.investigacion_formal.services.avance_service import AvanceService


class ObjetivoXPuntoViewSet(viewsets.ViewSet):
    serializer_class = ObjetivoXPuntoSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "agregar_avance"]:
            return [combinar(ROLES_CREACION_OPERATIVA), TieneAmbitoFormal(), ProyectoTieneActaInicio()]
        elif self.action in ["destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto, por_objetivo
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        registros = ObjetivoXPuntoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        registro = ObjetivoXPuntoService.obtener(pk)
        return Response(self.serializer_class(registro).data)

    def create(self, request):
        registro = ObjetivoXPuntoService.crear(
            objetivo_id=request.data.get("objetivo"),
            control=request.data.get("control"),
            peso=request.data.get("peso"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(registro).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="agregar-avance/(?P<punto_control_id>[^/.]+)")
    def agregar_avance(self, request, punto_control_id=None):
        registro, es_correccion = ObjetivoXPuntoService.agregar_avance(
            punto_control_id=punto_control_id,
            descripcion_avance=request.data.get("descripcion_avance"),
            avance=request.data.get("avance"),
            mes_avance=request.data.get("mes_avance"),
            anio_avance=request.data.get("anio_avance"),
            ejecutor=request.user,
        )
        proyecto_id = registro.objetivo.proyecto_id
        avance_ponderado = AvanceService.calcular_avance_ponderado(proyecto_id)
        return Response(
            {
                "registro": self.serializer_class(registro).data,
                "es_correccion_mismo_mes": es_correccion,
                "proyecto_id": proyecto_id,
                "avance_ponderado_proyecto": avance_ponderado,
            },
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, pk=None):
        ObjetivoXPuntoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        solo_activos = request.query_params.get("solo_activos", "true").lower() != "false"
        registros = ObjetivoXPuntoService.listar_por_proyecto(proyecto_id, solo_activos=solo_activos)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-objetivo/(?P<objetivo_id>[^/.]+)")
    def por_objetivo(self, request, objetivo_id=None):
        solo_activos = request.query_params.get("solo_activos", "true").lower() != "false"
        registros = ObjetivoXPuntoService.listar_por_objetivo(objetivo_id, solo_activos=solo_activos)
        return Response(self.serializer_class(registros, many=True).data)