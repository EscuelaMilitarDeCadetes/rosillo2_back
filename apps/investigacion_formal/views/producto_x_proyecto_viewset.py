from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formal.serializers.producto_x_proyecto_serializer import (
    ProductoXProyectoSerializer,
)
from apps.investigacion_formal.services.producto_x_proyecto_service import (
    ProductoXProyectoService,
)
from apps.investigacion_formal.permissions import (
    ROLES_CREACION_OPERATIVA, ROLES_ESCRITURA_GESTION, ROLES_LECTURA_INVESTIGACION_FORMAL, ProyectoTieneActaInicio, combinar,
)


class ProductoXProyectoViewSet(viewsets.ViewSet):
    serializer_class = ProductoXProyectoSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_CREACION_OPERATIVA), TieneAmbitoFormal(), ProyectoTieneActaInicio()]
        elif self.action in ["update", "destroy", "registrar_entrega", "subir_a_gruplac"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto, pendientes, entregados
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        productos = ProductoXProyectoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(productos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        producto = ProductoXProyectoService.obtener(pk)
        return Response(self.serializer_class(producto).data)

    def create(self, request):
        producto = ProductoXProyectoService.crear(
            producto_x_grupo_id=request.data.get("producto_x_grupo"),
            proyecto_id=request.data.get("proyecto"),
            categoria=request.data.get("categoria"),
            puntaje=request.data.get("puntaje"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(producto).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        producto = ProductoXProyectoService.actualizar(
            producto_x_proyecto_id=pk,
            ejecutor=request.user,
            categoria=request.data.get("categoria"),
            puntaje=request.data.get("puntaje"),
        )
        return Response(self.serializer_class(producto).data)

    def destroy(self, request, pk=None):
        ProductoXProyectoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="registrar-entrega")
    def registrar_entrega(self, request, pk=None):
        producto = ProductoXProyectoService.registrar_entrega(
            producto_x_proyecto_id=pk,
            archivo=request.FILES.get("archivo"),
            ip_creacion=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(producto).data)

    @action(detail=True, methods=["patch"], url_path="subir-gruplac")
    def subir_a_gruplac(self, request, pk=None):
        producto = ProductoXProyectoService.subir_a_gruplac(pk, ejecutor=request.user)
        return Response(self.serializer_class(producto).data)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        solo_activos = request.query_params.get("solo_activos", "true").lower() != "false"
        productos = ProductoXProyectoService.listar_por_proyecto(proyecto_id, solo_activos=solo_activos)
        return Response(self.serializer_class(productos, many=True).data)

    @action(detail=False, methods=["get"], url_path="pendientes/(?P<proyecto_id>[^/.]+)")
    def pendientes(self, request, proyecto_id=None):
        productos = ProductoXProyectoService.listar_pendientes_por_proyecto(proyecto_id)
        return Response(self.serializer_class(productos, many=True).data)

    @action(detail=False, methods=["get"], url_path="entregados/(?P<proyecto_id>[^/.]+)")
    def entregados(self, request, proyecto_id=None):
        productos = ProductoXProyectoService.listar_entregados_por_proyecto(proyecto_id)
        return Response(self.serializer_class(productos, many=True).data)