# apps/common/views/historial_viewset.py
from apps.common.pagination import CommonPageNumberPagination
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.usuarios.permissions.es_supervisor import EsSupervisor
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.serializers import HistorialSerializer
from apps.common.services.historial_service import HistorialService


class HistorialViewSet(viewsets.ViewSet):
    serializer_class = HistorialSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_lectura = ['list', 'retrieve', 'por_usuario', 'por_rango_fechas', 'buscar', 'acciones_sistema']
        if self.action in acciones_lectura:
            permission_classes = [EsSupervisor | EsSoporte]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        registros = HistorialService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        registro = HistorialService.obtener(pk)
        return Response(self.serializer_class(registro).data)

    @action(detail=False, methods=["get"], url_path="por-usuario/(?P<usuario_id>[^/.]+)")
    def por_usuario(self, request, usuario_id=None):
        registros = HistorialService.listar_por_usuario(usuario_id)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="acciones-sistema")
    def acciones_sistema(self, request):
        registros = HistorialService.listar_acciones_sistema()
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-rango-fechas")
    def por_rango_fechas(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        if not (fecha_inicio and fecha_fin):
            return Response(
                {"error": "Se requieren 'fecha_inicio' y 'fecha_fin'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        registros = HistorialService.listar_por_rango_fechas(fecha_inicio, fecha_fin)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="buscar")
    def buscar(self, request):
        filtros = dict(
            texto=request.query_params.get("q"),
            usuario_id=request.query_params.get("usuario_id"),
            fecha_inicio=request.query_params.get("fecha_inicio"),
            fecha_fin=request.query_params.get("fecha_fin"),
            solo_sistema=request.query_params.get("solo_sistema", "false").lower() == "true",
        )
        registros = HistorialService.buscar_con_filtros(filtros)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)