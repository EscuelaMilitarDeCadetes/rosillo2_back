from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.investigacion_formal.serializers.tipo_rubro_serializer import TipoRubroSerializer
from apps.investigacion_formal.services.tipo_rubro_service import TipoRubroService
from apps.investigacion_formal.permissions import ROLES_LECTURA_CATALOGOS, combinar
from apps.usuarios.permissions import EsSoporte


class TipoRubroViewSet(viewsets.ViewSet):
    serializer_class = TipoRubroSerializer
    pagination_class = InvestigacionFormalPageNumberPagination
    
    def get_permissions(self):
        if self.action in ["create", "update"]:
            return [EsSoporte(), TieneAmbitoFormal()]
        else:  # list, retrieve, aplicables
            return [combinar(ROLES_LECTURA_CATALOGOS), TieneAmbitoFormal()]

    def list(self, request):
        rubros = TipoRubroService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(rubros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        rubro = TipoRubroService.obtener(pk)
        return Response(self.serializer_class(rubro).data)

    def create(self, request):
        rubro = TipoRubroService.crear(
            nombre_rubro=request.data.get("nombre_rubro"),
            aplica=request.data.get("aplica"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(rubro).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        rubro = TipoRubroService.actualizar(
            tipo_rubro_id=pk,
            nombre_rubro=request.data.get("nombre_rubro"),
            aplica=request.data.get("aplica"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(rubro).data)

    @action(detail=False, methods=["get"], url_path="aplicables")
    def aplicables(self, request):
        rubros = TipoRubroService.listar_aplicables()
        return Response(self.serializer_class(rubros, many=True).data)