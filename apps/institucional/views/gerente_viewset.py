from apps.institucional.pagination import InstitucionalPageNumberPagination
from apps.institucional.selectors.gerente_selector import GerenteSelector
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.institucional.serializers import GerenteSerializer
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.institucional.services.gerente_service import GerenteService


class GerenteViewSet(viewsets.ViewSet):
    """
    Adaptador HTTP puro: toda la lógica vive en GerenteService.

    POST /gerentes/ -> GerenteService.crear() (asigna nuevo Gerente,
    cerrando automáticamente al anterior si existe).
    GET  /gerentes/actual/ -> acción especial para obtener_actual().
    """
    serializer_class = GerenteSerializer
    pagination_class = InstitucionalPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'actual', 'historico']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsSoporte | EsCInterno]
        return [permission() for permission in permission_classes]

    def list(self, request):
        gerentes = GerenteService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(gerentes, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        gerente = GerenteService.obtener(pk)
        serializer = self.serializer_class(gerente)
        return Response(serializer.data)

    def create(self, request):
        gerente = GerenteService.crear(
            persona_id=request.data.get("persona"),
            ejecutor=request.user,
            fecha_ingreso=request.data.get("fecha_ingreso"),
        )
        serializer = self.serializer_class(gerente)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        gerente = GerenteService.actualizar(
            gerente_id=pk,
            ejecutor=request.user,
            fecha_ingreso=request.data.get("fecha_ingreso"),
            fecha_salida=request.data.get("fecha_salida"),
        )
        serializer = self.serializer_class(gerente)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        GerenteService.eliminar(pk, ejecutor=request.user)
        return Response(status=204)

    @action(detail=False, methods=["get"])
    def actual(self, request):
        gerente = GerenteService.obtener_actual()
        if gerente is None:
            return Response(status=204)
        serializer = self.serializer_class(gerente)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def historico(self, request):
        gerentes = GerenteSelector.listar_historico()
        serializer = self.serializer_class(gerentes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def finalizar(self, request, pk=None):
        gerente = GerenteService.finalizar(
            gerente_id=pk,
            ejecutor=request.user,
            fecha_salida=request.data.get("fecha_salida"),
        )
        serializer = self.serializer_class(gerente)
        return Response(serializer.data)