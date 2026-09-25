# apps/investigacion_formativa/views/evaluacion_proceso_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.evaluacion_proceso_serializer import EvaluacionProcesoSerializer
from apps.investigacion_formativa.services.evaluacion_proceso_service import EvaluacionProcesoService
from apps.investigacion_formativa.permissions import (
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
)
from apps.usuarios.permissions import EsTutor, EsJurado, EsFacultad, EsDecano, EsSoporte


class EvaluacionProcesoViewSet(viewsets.ViewSet):
    serializer_class = EvaluacionProcesoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            # Solo quien califica (Tutor/Jurado) puede emitir una evaluación
            return [combinar([EsTutor, EsJurado, EsFacultad, EsDecano, EsSoporte]), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_instancia_etapa, por_proceso
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        evaluaciones = EvaluacionProcesoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(evaluaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        evaluacion = EvaluacionProcesoService.obtener(pk)
        return Response(self.serializer_class(evaluacion).data)

    def create(self, request):
        evaluacion = EvaluacionProcesoService.crear(
            evaluador_id=request.data.get("evaluador"),
            instancia_etapa_id=request.data.get("instancia_etapa"),
            concepto=request.data.get("concepto"),
            nota=request.data.get("nota"),
            peso=request.data.get("peso"),
            aprobado=request.data.get("aprobado"),
            resultado=request.data.get("resultado"),
            tipo_evaluador=request.data.get("tipo_evaluador"),
            tipo_evaluacion=request.data.get("tipo_evaluacion"),
            es_tercer_evaluador=request.data.get("es_tercer_evaluador", False),
            observaciones=request.data.get("observaciones"),
            rubrica_evaluacion=request.data.get("rubrica_evaluacion", ""),
            criterio_rubrica=request.data.get("criterio_rubrica", ""),
            resultado_criterio=request.data.get("resultado_criterio", ""),
            ejecutor=request.user,
            usuario_revisor_id=request.data.get("usuario_revisor"),
        )
        return Response(self.serializer_class(evaluacion).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="por-instancia-etapa/(?P<instancia_etapa_id>[^/.]+)")
    def por_instancia_etapa(self, request, instancia_etapa_id=None):
        evaluaciones = EvaluacionProcesoService.listar_por_instancia_etapa(instancia_etapa_id)
        return Response(self.serializer_class(evaluaciones, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        evaluaciones = EvaluacionProcesoService.listar_por_proceso(proceso_id)
        return Response(self.serializer_class(evaluaciones, many=True).data)

    @action(detail=False, methods=["get"], url_path="terceros-evaluadores/(?P<proceso_id>[^/.]+)")
    def terceros_evaluadores(self, request, proceso_id=None):
        evaluaciones = EvaluacionProcesoService.listar_terceros_evaluadores(proceso_id)
        return Response(self.serializer_class(evaluaciones, many=True).data)