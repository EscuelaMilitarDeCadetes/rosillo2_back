from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.plan_trabajo_serializer import PlanTrabajoSerializer
from apps.investigacion_formativa.services.plan_trabajo_service import PlanTrabajoService
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_AUTOR_PLAN_TRABAJO,
    ROLES_APROBACION_PLAN_TRABAJO, combinar,
)


class PlanTrabajoViewSet(viewsets.ViewSet):
    serializer_class = PlanTrabajoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "enviar", "destroy"]:
            return [combinar(ROLES_AUTOR_PLAN_TRABAJO), TieneAmbitoFormativa()]
        elif self.action in ["aprobar", "rechazar"]:
            return [combinar(ROLES_APROBACION_PLAN_TRABAJO), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_proceso
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        planes = PlanTrabajoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(planes, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        plan = PlanTrabajoService.obtener(pk)
        return Response(self.serializer_class(plan).data)

    def create(self, request):
        plan = PlanTrabajoService.crear(
            proceso_id=request.data.get("proceso"),
            descripcion_general=request.data.get("descripcion_general"),
            objetivo_general=request.data.get("objetivo_general"),
            actividades_planeadas=request.data.get("actividades_planeadas"),
            fecha_inicio_planeada=request.data.get("fecha_inicio_planeada"),
            fecha_fin_planeada=request.data.get("fecha_fin_planeada"),
            ejecutor=request.user,
            observaciones=request.data.get("observaciones"),
        )
        return Response(self.serializer_class(plan).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        plan = PlanTrabajoService.actualizar(
            plan_trabajo_id=pk,
            descripcion_general=request.data.get("descripcion_general"),
            objetivo_general=request.data.get("objetivo_general"),
            actividades_planeadas=request.data.get("actividades_planeadas"),
            fecha_inicio_planeada=request.data.get("fecha_inicio_planeada"),
            fecha_fin_planeada=request.data.get("fecha_fin_planeada"),
            ejecutor=request.user,
            observaciones=request.data.get("observaciones"),
        )
        return Response(self.serializer_class(plan).data)

    def destroy(self, request, pk=None):
        PlanTrabajoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def enviar(self, request, pk=None):
        plan = PlanTrabajoService.enviar(pk, ejecutor=request.user)
        return Response(self.serializer_class(plan).data)

    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        plan = PlanTrabajoService.aprobar(
            plan_trabajo_id=pk,
            aprobado_por_id=request.user.pk,
            ejecutor=request.user,
        )
        return Response(self.serializer_class(plan).data)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        plan = PlanTrabajoService.rechazar(
            plan_trabajo_id=pk,
            observaciones=request.data.get("observaciones"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(plan).data)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        plan = PlanTrabajoService.obtener_por_proceso(proceso_id)
        if plan is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(self.serializer_class(plan).data)