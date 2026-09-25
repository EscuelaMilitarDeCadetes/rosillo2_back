from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formal.serializers.calificacion_serializer import CalificacionSerializer
from apps.investigacion_formal.services.calificacion_service import CalificacionService
from apps.investigacion_formal.permissions import ROLES_CONSULTA_CALIFICACION, combinar
from apps.usuarios.permissions import EsCInterno, EsSoporte, TieneAmbitoFormal


class CalificacionViewSet(viewsets.ViewSet):
    serializer_class = CalificacionSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        acciones_autoservicio = ['list', 'retrieve', 'por_proyecto_convocatoria']
        if self.action in acciones_autoservicio:
            return [combinar(ROLES_CONSULTA_CALIFICACION), TieneAmbitoFormal()]   # antes: inline [EsSupervisor | EsCInterno | EsCExterno]
        elif self.action in ['calificar']:
            return [EsCInterno(), TieneAmbitoFormal()]
        else:  # create
            return [EsSoporte(), TieneAmbitoFormal()]

    def list(self, request):
        calificaciones = CalificacionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(calificaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        calificacion = CalificacionService.obtener(pk)
        return Response(self.serializer_class(calificacion).data)

    def create(self, request):
        calificacion = CalificacionService.crear(
            fase_id=request.data.get("fase"),
            aplicar_id=request.data.get("aplicar"),
            ejecutor=request.user,
            observacion=request.data.get("observacion", ""),
        )
        return Response(self.serializer_class(calificacion).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="calificar")
    def calificar(self, request, pk=None):
        calificacion = CalificacionService.calificar_fase(
            calificacion_id=pk,
            aprobado=request.data.get("aprobado"),
            observacion=request.data.get("observacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(calificacion).data)

    @action(detail=False, methods=["get"], url_path="por-proyecto-convocatoria/(?P<aplicar_id>[^/.]+)")
    def por_proyecto_convocatoria(self, request, aplicar_id=None):
        calificaciones = CalificacionService.listar_por_proyecto_x_convocatoria(aplicar_id)
        return Response(self.serializer_class(calificaciones, many=True).data)