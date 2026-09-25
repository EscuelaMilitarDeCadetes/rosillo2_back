from apps.common.pagination import CommonPageNumberPagination
from apps.usuarios.permissions.es_cexterno import EsCExterno
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_decano import EsDecano
from apps.usuarios.permissions.es_facultad import EsFacultad
from apps.usuarios.permissions.es_grupo import EsGrupo
from apps.usuarios.permissions.es_supervisor import EsSupervisor
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.serializers import AprobacionSerializer
from apps.common.services.aprobacion_service import AprobacionService


class AprobacionViewSet(viewsets.ViewSet):
    serializer_class = AprobacionSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_autoservicio = ['list', 'retrieve', 'pendientes', 'por_documento', 'ultima_por_documento']
        if self.action in acciones_autoservicio:
            permission_classes = [EsDecano | EsSupervisor | EsFacultad | EsGrupo | EsCInterno | EsCExterno]
        elif self.action in ['aprobar', 'rechazar']:
            permission_classes = [EsDecano | EsSupervisor]
        else:  # create
            permission_classes = [EsFacultad | EsGrupo | EsCInterno | EsCExterno]
        return [permission() for permission in permission_classes]

    def list(self, request):
        aprobaciones = AprobacionService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(aprobaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        aprobacion = AprobacionService.obtener(pk)
        return Response(self.serializer_class(aprobacion).data)

    def create(self, request):
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=request.data.get("usuario_revisor"),
            tipo_documento_id=request.data.get("tipo_documento"),
            id_documento=request.data.get("id_documento"),
            ejecutor=request.user,
            estado=request.data.get("estado", "PENDIENTE"),
            observacion=request.data.get("observacion"),
        )
        return Response(self.serializer_class(aprobacion).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        aprobacion = AprobacionService.aprobar(
            pk, ejecutor=request.user, observacion=request.data.get("observacion")
        )
        return Response(self.serializer_class(aprobacion).data)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        aprobacion = AprobacionService.rechazar(
            pk, ejecutor=request.user, observacion=request.data.get("observacion")
        )
        return Response(self.serializer_class(aprobacion).data)

    @action(detail=False, methods=["get"])
    def pendientes(self, request):
        usuario_revisor_id = request.query_params.get("usuario_revisor")
        aprobaciones = AprobacionService.listar_pendientes(usuario_revisor_id)
        return Response(self.serializer_class(aprobaciones, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-documento")
    def por_documento(self, request):
        tipo_documento_id = request.query_params.get("tipo_documento")
        id_documento = request.query_params.get("id_documento")
        aprobaciones = AprobacionService.listar_por_documento(tipo_documento_id, id_documento)
        return Response(self.serializer_class(aprobaciones, many=True).data)

    @action(detail=False, methods=["get"], url_path="ultima-por-documento")
    def ultima_por_documento(self, request):
        tipo_documento_id = request.query_params.get("tipo_documento")
        id_documento = request.query_params.get("id_documento")
        aprobacion = AprobacionService.obtener_ultima_por_documento(tipo_documento_id, id_documento)
        if aprobacion is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.serializer_class(aprobacion).data)