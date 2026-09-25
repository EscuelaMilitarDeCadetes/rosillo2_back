# apps/investigacion_formativa/views/certificacion_externa_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.certificacion_externa_serializer import CertificacionExternaSerializer
from apps.investigacion_formativa.services.certificacion_externa_service import CertificacionExternaService
from apps.investigacion_formativa.permissions import (
    ROLES_AUTOR_CERTIFICACION_EXTERNA,
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
)


class CertificacionExternaViewSet(viewsets.ViewSet):
    serializer_class = CertificacionExternaSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "certificado_asistencia", "destroy"]:
            # El propio estudiante crea/adjunta su certificación, o Facultad/Decano en su nombre
            return [combinar(ROLES_AUTOR_CERTIFICACION_EXTERNA), TieneAmbitoFormativa()]  # <- antes: ROLES_CREACION_OPERATIVA
        if self.action in ["certificado_aprobacion", "validar_horas"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        else:
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        certificaciones = CertificacionExternaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(certificaciones, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        certificacion = CertificacionExternaService.obtener(pk)
        return Response(self.serializer_class(certificacion).data)

    def create(self, request):
        certificacion = CertificacionExternaService.crear(
            proceso_id=request.data.get("proceso"),
            tipo=request.data.get("tipo"),
            nombre_programa=request.data.get("nombre_programa"),
            institucion=request.data.get("institucion"),
            horas_certificadas=request.data.get("horas_certificadas"),
            fecha_inicio=request.data.get("fecha_inicio"),
            fecha_fin=request.data.get("fecha_fin"),
            certificado_asistencia_id=request.data.get("certificado_asistencia"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(certificacion).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        certificacion = CertificacionExternaService.actualizar(
            certificacion_id=pk,
            tipo=request.data.get("tipo"),
            nombre_programa=request.data.get("nombre_programa"),
            institucion=request.data.get("institucion"),
            horas_certificadas=request.data.get("horas_certificadas"),
            fecha_inicio=request.data.get("fecha_inicio"),
            fecha_fin=request.data.get("fecha_fin"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(certificacion).data)

    def destroy(self, request, pk=None):
        CertificacionExternaService.eliminar(certificacion_id=pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-proceso/(?P<proceso_id>[^/.]+)")
    def por_proceso(self, request, proceso_id=None):
        certificaciones = CertificacionExternaService.listar_por_proceso(proceso_id)
        return Response(self.serializer_class(certificaciones, many=True).data)

    @action(detail=False, methods=["get"], url_path="pendientes-validacion")
    def pendientes_validacion(self, request):
        proceso_id = request.query_params.get("proceso")
        certificaciones = CertificacionExternaService.listar_pendientes_validacion(proceso_id=proceso_id)
        return Response(self.serializer_class(certificaciones, many=True).data)

    @action(detail=True, methods=["patch"], url_path="certificado-asistencia")
    def certificado_asistencia(self, request, pk=None):
        certificacion = CertificacionExternaService.adjuntar_certificado_asistencia(
            certificacion_id=pk,
            certificado_asistencia_id=request.data.get("documento"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(certificacion).data)

    @action(detail=True, methods=["patch"], url_path="certificado-aprobacion")
    def certificado_aprobacion(self, request, pk=None):
        certificacion = CertificacionExternaService.adjuntar_certificado_aprobacion(
            certificacion_id=pk,
            certificado_aprobacion_id=request.data.get("documento"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(certificacion).data)

    @action(detail=True, methods=["patch"], url_path="validar-horas")
    def validar_horas(self, request, pk=None):
        certificacion = CertificacionExternaService.validar_horas(
            certificacion_id=pk,
            horas_validadas=request.data.get("horas_validadas"),
            validado_por_id=request.user.id,
            ejecutor=request.user,
        )
        return Response(self.serializer_class(certificacion).data)