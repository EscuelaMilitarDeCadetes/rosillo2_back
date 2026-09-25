from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.participante_proceso_serializer import (
    ParticipanteProcesoSerializer,
)
from apps.investigacion_formativa.services.participante_proceso_service import (
    ParticipanteProcesoService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_CREACION_OPERATIVA, combinar,
)


class ParticipanteProcesoViewSet(viewsets.ViewSet):
    serializer_class = ParticipanteProcesoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "finalizar", "destroy"]:
            return [combinar(ROLES_CREACION_OPERATIVA), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_proceso
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]    

    def list(self, request):
        participantes = ParticipanteProcesoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(participantes, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        participante = ParticipanteProcesoService.obtener(pk)
        return Response(self.serializer_class(participante).data)

    def create(self, request):
        participante = ParticipanteProcesoService.crear(
            proceso_formativo_id=request.data.get("proceso_formativo"),
            persona_id=request.data.get("persona"),
            rol_en_modalidad=request.data.get("rol_en_modalidad"),
            ejecutor=request.user,
            fecha_finalizacion=request.data.get("fecha_finalizacion"),
            usuario_revisor_id=request.data.get("usuario_revisor"),
        )
        return Response(self.serializer_class(participante).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        participante = ParticipanteProcesoService.actualizar(
            participante_id=pk,
            rol_en_modalidad=request.data.get("rol_en_modalidad"),
            ejecutor=request.user,
            fecha_finalizacion=request.data.get("fecha_finalizacion"),
        )
        return Response(self.serializer_class(participante).data)

    def destroy(self, request, pk=None):
        ParticipanteProcesoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def finalizar(self, request, pk=None):
        participante = ParticipanteProcesoService.finalizar(pk, ejecutor=request.user)
        return Response(self.serializer_class(participante).data)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_formativo_id>[^/.]+)")
    def por_proceso(self, request, proceso_formativo_id=None):
        participantes = ParticipanteProcesoService.listar_por_proceso(proceso_formativo_id)
        return Response(self.serializer_class(participantes, many=True).data)