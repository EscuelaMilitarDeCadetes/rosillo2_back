# apps/investigacion_formativa/views/etapa_flujo_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.etapa_flujo_serializer import EtapaFlujoSerializer
from apps.investigacion_formativa.services.etapa_flujo_service import EtapaFlujoService
from apps.investigacion_formativa.permissions import (
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
)


class EtapaFlujoViewSet(viewsets.ViewSet):
    serializer_class = EtapaFlujoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "activar", "desactivar"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_flujo
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        etapas = EtapaFlujoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(etapas, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        etapa = EtapaFlujoService.obtener(pk)
        return Response(self.serializer_class(etapa).data)

    def create(self, request):
        etapa = EtapaFlujoService.crear(
            flujo_id=request.data.get("flujo"),
            nombre=request.data.get("nombre"),
            descripcion=request.data.get("descripcion"),
            orden=request.data.get("orden"),
            codigo=request.data.get("codigo"),
            tipo_etapa=request.data.get("tipo_etapa"),
            rol_responsable=request.data.get("rol_responsable"),
            documento_requerido_id=request.data.get("documento_requerido"),
            es_obligatoria=request.data.get("es_obligatoria", True),
            permite_paralelismo=request.data.get("permite_paralelismo", True),
            permite_reversion=request.data.get("permite_reversion", True),
            permite_salto=request.data.get("permite_salto", True),
            requiere_aprobacion=request.data.get("requiere_aprobacion", True),
            requiere_documento=request.data.get("requiere_documento", True),
            requiere_firma=request.data.get("requiere_firma", True),
            requiere_evaluacion=request.data.get("requiere_evaluacion", True),
            es_final=request.data.get("es_final", False),
            permite_reintentos=request.data.get("permite_reintentos", True),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(etapa).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        etapa = EtapaFlujoService.actualizar(
            etapa_id=pk,
            nombre=request.data.get("nombre"),
            descripcion=request.data.get("descripcion"),
            orden=request.data.get("orden"),
            codigo=request.data.get("codigo"),
            tipo_etapa=request.data.get("tipo_etapa"),
            rol_responsable=request.data.get("rol_responsable"),
            documento_requerido_id=request.data.get("documento_requerido"),
            es_obligatoria=request.data.get("es_obligatoria", True),
            permite_paralelismo=request.data.get("permite_paralelismo", True),
            permite_reversion=request.data.get("permite_reversion", True),
            permite_salto=request.data.get("permite_salto", True),
            requiere_aprobacion=request.data.get("requiere_aprobacion", True),
            requiere_documento=request.data.get("requiere_documento", True),
            requiere_firma=request.data.get("requiere_firma", True),
            requiere_evaluacion=request.data.get("requiere_evaluacion", True),
            es_final=request.data.get("es_final", False),
            permite_reintentos=request.data.get("permite_reintentos", True),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(etapa).data)

    @action(detail=False, methods=["get"], url_path="por-flujo/(?P<flujo_id>[^/.]+)")
    def por_flujo(self, request, flujo_id=None):
        etapas = EtapaFlujoService.listar_por_flujo(flujo_id)
        return Response(self.serializer_class(etapas, many=True).data)

    @action(detail=True, methods=["patch"], url_path="activar")
    def activar(self, request, pk=None):
        etapa = EtapaFlujoService.activar(etapa_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(etapa).data)

    @action(detail=True, methods=["patch"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        etapa = EtapaFlujoService.desactivar(etapa_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(etapa).data)