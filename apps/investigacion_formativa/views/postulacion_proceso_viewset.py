from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.postulacion_proceso_serializer import (
    PostulacionProcesoSerializer,
)
from apps.investigacion_formativa.services.postulacion_proceso_service import (
    PostulacionProcesoService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_AUTOR_POSTULACION,
    ROLES_VALIDACION_POSTULACION, ROLES_DECISION_DIRECTA_DECANO,
    ROLES_SOLICITUD_APROBACION_FACULTAD, ROLES_CONFIRMACION_DECANO, combinar,
)
from apps.common.serializers import AprobacionSerializer


class PostulacionProcesoViewSet(viewsets.ViewSet):
    serializer_class = PostulacionProcesoSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "enviar", "destroy"]:
            return [combinar(ROLES_AUTOR_POSTULACION), TieneAmbitoFormativa()]
        elif self.action == "pasar_a_validacion":
            return [combinar(ROLES_VALIDACION_POSTULACION), TieneAmbitoFormativa()]
        elif self.action in ["aprobar", "rechazar"]:
            # Decisión DIRECTA sobre la postulación: Decano/Soporte. Facultad
            # ya NO puede aprobar/rechazar por sí sola — debe pasar por
            # 'solicitar_decision_decano'.
            return [combinar(ROLES_DECISION_DIRECTA_DECANO), TieneAmbitoFormativa()]
        elif self.action == "solicitar_decision_decano":
            return [combinar(ROLES_SOLICITUD_APROBACION_FACULTAD), TieneAmbitoFormativa()]
        elif self.action in ["confirmar_aprobacion_decano", "denegar_por_decano"]:
            return [combinar(ROLES_CONFIRMACION_DECANO), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_estudiante, pendientes_por_facultad
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        postulaciones = PostulacionProcesoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(postulaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        postulacion = PostulacionProcesoService.obtener(pk)
        return Response(self.serializer_class(postulacion).data)

    def create(self, request):
        postulacion = PostulacionProcesoService.crear(
            estudiante_id=request.data.get("estudiante"),
            modalidad_id=request.data.get("modalidad"),
            promedio_actual=request.data.get("promedio_actual"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(postulacion).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        postulacion = PostulacionProcesoService.actualizar(
            postulacion_id=pk,
            promedio_actual=request.data.get("promedio_actual"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(postulacion).data)

    def destroy(self, request, pk=None):
        PostulacionProcesoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def enviar(self, request, pk=None):
        postulacion = PostulacionProcesoService.enviar(pk, ejecutor=request.user)
        return Response(self.serializer_class(postulacion).data)

    @action(detail=True, methods=["post"], url_path="pasar-a-validacion")
    def pasar_a_validacion(self, request, pk=None):
        postulacion = PostulacionProcesoService.pasar_a_validacion(pk, ejecutor=request.user)
        return Response(self.serializer_class(postulacion).data)

    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        """Decisión DIRECTA (Decano/Soporte). Si quien decide es Facultad,
        usar 'solicitar-decision-decano' en su lugar."""
        postulacion = PostulacionProcesoService.aprobar(
            postulacion_id=pk,
            flujo_version_id=request.data.get("flujo_version"),
            titulo=request.data.get("titulo"),
            observacion=request.data.get("observacion"),
            fecha_inicio=request.data.get("fecha_inicio"),
            fecha_fin=request.data.get("fecha_fin"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(postulacion).data)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        """Decisión DIRECTA (Decano/Soporte). Si quien decide es Facultad,
        usar 'solicitar-decision-decano' en su lugar."""
        postulacion = PostulacionProcesoService.rechazar(
            postulacion_id=pk,
            observacion_coordinacion=request.data.get("observacion_coordinacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(postulacion).data)

    @action(detail=True, methods=["post"], url_path="solicitar-decision-decano")
    def solicitar_decision_decano(self, request, pk=None):
        """Facultad solicita al Decano que decida (aprobar/rechazar) sobre
        una postulación en 'EN_VALIDACION'. No cambia el estado de la
        postulación: abre una Aprobacion pendiente."""
        aprobacion = PostulacionProcesoService.solicitar_decision_decano(
            postulacion_id=pk,
            usuario_revisor_id=request.data.get("usuario_revisor"),
            ejecutor=request.user,
            observacion=request.data.get("observacion"),
        )
        return Response(AprobacionSerializer(aprobacion).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=["post"],
        url_path="confirmar-aprobacion-decano/(?P<aprobacion_id>[^/.]+)",
    )
    def confirmar_aprobacion_decano(self, request, aprobacion_id=None):
        """El Decano confirma una solicitud abierta por Facultad: aprueba la
        Aprobacion y genera el ProcesoFormativo asociado."""
        postulacion = PostulacionProcesoService.confirmar_aprobacion_decano(
            aprobacion_id=aprobacion_id,
            flujo_version_id=request.data.get("flujo_version"),
            titulo=request.data.get("titulo"),
            observacion=request.data.get("observacion"),
            fecha_inicio=request.data.get("fecha_inicio"),
            fecha_fin=request.data.get("fecha_fin"),
            ejecutor=request.user,
            observacion_decano=request.data.get("observacion_decano"),
        )
        return Response(self.serializer_class(postulacion).data)

    @action(
        detail=False, methods=["post"],
        url_path="denegar-por-decano/(?P<aprobacion_id>[^/.]+)",
    )
    def denegar_por_decano(self, request, aprobacion_id=None):
        """El Decano deniega una solicitud abierta por Facultad: rechaza la
        Aprobacion y rechaza la postulación."""
        postulacion = PostulacionProcesoService.denegar_por_decano(
            aprobacion_id=aprobacion_id,
            ejecutor=request.user,
            observacion=request.data.get("observacion"),
        )
        return Response(self.serializer_class(postulacion).data)

    @action(detail=False, methods=["get"], url_path="por-estudiante/(?P<estudiante_id>[^/.]+)")
    def por_estudiante(self, request, estudiante_id=None):
        postulaciones = PostulacionProcesoService.listar_por_estudiante(estudiante_id)
        return Response(self.serializer_class(postulaciones, many=True).data)

    @action(detail=False, methods=["get"], url_path="pendientes-por-facultad/(?P<facultad_id>[^/.]+)")
    def pendientes_por_facultad(self, request, facultad_id=None):
        postulaciones = PostulacionProcesoService.listar_pendientes_por_facultad(facultad_id)
        return Response(self.serializer_class(postulaciones, many=True).data)