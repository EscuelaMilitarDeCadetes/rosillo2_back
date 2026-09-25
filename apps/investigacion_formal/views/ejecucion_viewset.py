from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formal.serializers.ejecucion_serializer import EjecucionSerializer
from apps.investigacion_formal.services.ejecucion_service import EjecucionService
from apps.investigacion_formal.permissions import ROLES_LECTURA_INVESTIGACION_FORMAL, combinar
from apps.usuarios.permissions import EsCInterno, EsCExterno, TieneAmbitoFormal


class EjecucionViewSet(viewsets.ViewSet):
    serializer_class = EjecucionSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            permission_classes = [EsCInterno | EsCExterno]
            return [permission() for permission in permission_classes] + [TieneAmbitoFormal()]
        else:  # list, retrieve, por_monto
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        ejecuciones = EjecucionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(ejecuciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        ejecucion = EjecucionService.obtener(pk)
        return Response(self.serializer_class(ejecucion).data)

    def create(self, request):
        ejecucion = EjecucionService.crear(
            monto_id=request.data.get("monto"),
            tipo_rubro_id=request.data.get("tipo_rubro"),
            nombre=request.data.get("nombre"),
            costo=request.data.get("costo"),
            descripcion=request.data.get("descripcion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(ejecucion).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        ejecucion = EjecucionService.actualizar(
            ejecucion_id=pk,
            ejecutor=request.user,
            monto_id=request.data.get("monto"),
            tipo_rubro_id=request.data.get("tipo_rubro"),
            nombre=request.data.get("nombre"),
            costo=request.data.get("costo"),
            descripcion=request.data.get("descripcion"),
        )
        return Response(self.serializer_class(ejecucion).data)

    def destroy(self, request, pk=None):
        EjecucionService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-monto/(?P<monto_id>[^/.]+)")
    def por_monto(self, request, monto_id=None):
        solo_activas = request.query_params.get("solo_activas", "true").lower() != "false"
        ejecuciones = EjecucionService.listar_por_monto(monto_id, solo_activas=solo_activas)
        return Response(self.serializer_class(ejecuciones, many=True).data)