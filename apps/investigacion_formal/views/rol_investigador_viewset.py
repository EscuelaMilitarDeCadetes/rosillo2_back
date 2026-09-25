from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.investigacion_formal.permissions import ROLES_LECTURA_CATALOGOS, combinar
from apps.investigacion_formal.serializers.rol_investigador_serializer import (
    RolInvestigadorSerializer,
)
from apps.investigacion_formal.services.rol_investigador_service import RolInvestigadorService
from apps.usuarios.permissions import EsSoporte


class RolInvestigadorViewSet(viewsets.ViewSet):
    serializer_class = RolInvestigadorSerializer
    pagination_class = InvestigacionFormalPageNumberPagination
    
    def get_permissions(self):
        if self.action in ["create", "update"]:
            return [EsSoporte(), TieneAmbitoFormal()]
        else:  # list, retrieve
            return [combinar(ROLES_LECTURA_CATALOGOS), TieneAmbitoFormal()]

    def list(self, request):
        roles = RolInvestigadorService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(roles, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        rol = RolInvestigadorService.obtener(pk)
        return Response(self.serializer_class(rol).data)

    def create(self, request):
        rol = RolInvestigadorService.crear(
            nombre_rol_investigador=request.data.get("nombre_rol_investigador"),
            descripcion=request.data.get("descripcion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(rol).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        rol = RolInvestigadorService.actualizar(
            rol_investigador_id=pk,
            nombre_rol_investigador=request.data.get("nombre_rol_investigador"),
            descripcion=request.data.get("descripcion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(rol).data)