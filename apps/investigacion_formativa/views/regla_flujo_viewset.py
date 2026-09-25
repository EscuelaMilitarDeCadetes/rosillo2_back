# apps/investigacion_formativa/views/regla_flujo_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.regla_flujo_serializer import ReglaFlujoSerializer
from apps.investigacion_formativa.services.regla_flujo_service import ReglaFlujoService
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_CONFIGURACION_FLUJO, combinar,
)


class ReglaFlujoViewSet(viewsets.ViewSet):
    serializer_class = ReglaFlujoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "activar", "desactivar"]:
            return [combinar(ROLES_CONFIGURACION_FLUJO), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_transicion
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        reglas = ReglaFlujoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(reglas, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        regla = ReglaFlujoService.obtener(pk)
        return Response(self.serializer_class(regla).data)

    def create(self, request):
        regla = ReglaFlujoService.crear(
            etapa_origen_id=request.data.get("etapa_origen"),
            etapa_destino_id=request.data.get("etapa_destino"),
            nombre=request.data.get("nombre"),
            operador=request.data.get("operador"),
            tipo_regla=request.data.get("tipo_regla"),
            valor_minimo=request.data.get("valor_minimo"),
            valor_maximo=request.data.get("valor_maximo"),
            mensaje_error=request.data.get("mensaje_error"),
            accion_resultado=request.data.get("accion_resultado"),
            descripcion=request.data.get("descripcion"),
            fecha_inicio=request.data.get("fecha_inicio"),
            ejecutor=request.user,
            fecha_fin=request.data.get("fecha_fin"),
            bloqueante=request.data.get("bloqueante", False),
            prioridad=request.data.get("prioridad", 1),
        )
        return Response(self.serializer_class(regla).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        regla = ReglaFlujoService.actualizar(
            regla_id=pk,
            etapa_origen_id=request.data.get("etapa_origen"),
            etapa_destino_id=request.data.get("etapa_destino"),
            nombre=request.data.get("nombre"),
            operador=request.data.get("operador"),
            tipo_regla=request.data.get("tipo_regla"),
            valor_minimo=request.data.get("valor_minimo"),
            valor_maximo=request.data.get("valor_maximo"),
            mensaje_error=request.data.get("mensaje_error"),
            accion_resultado=request.data.get("accion_resultado"),
            descripcion=request.data.get("descripcion"),
            fecha_inicio=request.data.get("fecha_inicio"),
            ejecutor=request.user,
            fecha_fin=request.data.get("fecha_fin"),
            prioridad=request.data.get("prioridad", 1),
        )
        return Response(self.serializer_class(regla).data)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        regla = ReglaFlujoService.activar(pk, ejecutor=request.user)
        return Response(self.serializer_class(regla).data)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        regla = ReglaFlujoService.desactivar(pk, ejecutor=request.user)
        return Response(self.serializer_class(regla).data)

    @action(
        detail=False, methods=["get"],
        url_path="por-transicion/(?P<etapa_origen_id>[^/.]+)/(?P<etapa_destino_id>[^/.]+)",
    )
    def por_transicion(self, request, etapa_origen_id=None, etapa_destino_id=None):
        reglas = ReglaFlujoService.listar_por_transicion(etapa_origen_id, etapa_destino_id)
        return Response(self.serializer_class(reglas, many=True).data)