# E:\PROYECTO_ROSILLO\django_react\django\rosillo\apps\investigacion_formativa\views\segunda_instancia_viewset.py

from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.segunda_instancia_serializer import (
    SegundaInstanciaSerializer,
)
from apps.investigacion_formativa.services.segunda_instancia_service import (
    SegundaInstanciaService,
)
from apps.investigacion_formativa.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMATIVA, ROLES_ESCRITURA_GESTION,
    ROLES_CALIFICACION_PROCESO, ROLES_DECISION_DIRECTA_DECANO,
    ROLES_SOLICITUD_APROBACION_FACULTAD, ROLES_CONFIRMACION_DECANO, combinar,
)
from apps.common.serializers import AprobacionSerializer


class SegundaInstanciaViewSet(viewsets.ViewSet):
    serializer_class = SegundaInstanciaSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_CALIFICACION_PROCESO), TieneAmbitoFormativa()]
        elif self.action == "activar":
            # Activación DIRECTA: Decano/Soporte. Facultad ya NO activa por
            # sí sola — debe pasar por 'solicitar_activacion_decano'.
            return [combinar(ROLES_DECISION_DIRECTA_DECANO), TieneAmbitoFormativa()]
        elif self.action in ["consumir", "destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        elif self.action == "solicitar_activacion_decano":
            return [combinar(ROLES_SOLICITUD_APROBACION_FACULTAD), TieneAmbitoFormativa()]
        elif self.action in ["confirmar_activacion_decano", "denegar_activacion_decano"]:
            return [combinar(ROLES_CONFIRMACION_DECANO), TieneAmbitoFormativa()]
        else:  # list, retrieve, activadas_pendientes
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        instancias = SegundaInstanciaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(instancias, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        instancia = SegundaInstanciaService.obtener(pk)
        return Response(self.serializer_class(instancia).data)

    def create(self, request):
        instancia = SegundaInstanciaService.crear(
            proceso_id=request.data.get("proceso"),
            instancia_etapa_id=request.data.get("instancia_etapa"),
            evaluacion_id=request.data.get("evaluacion"),
            etapa_retorno_id=request.data.get("etapa_retorno"),
            tipo=request.data.get("tipo"),
            motivo=request.data.get("motivo"),
            ejecutor=request.user,
            nota_maxima=request.data.get("nota_maxima", 3.5),
        )
        return Response(self.serializer_class(instancia).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        SegundaInstanciaService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        """Activación DIRECTA (Decano/Soporte). Si quien decide es Facultad,
        usar 'solicitar-activacion-decano' en su lugar."""
        instancia = SegundaInstanciaService.activar(pk, ejecutor=request.user)
        return Response(self.serializer_class(instancia).data)

    @action(detail=True, methods=["post"])
    def consumir(self, request, pk=None):
        instancia = SegundaInstanciaService.consumir(pk, ejecutor=request.user)
        return Response(self.serializer_class(instancia).data)

    @action(detail=True, methods=["post"], url_path="solicitar-activacion-decano")
    def solicitar_activacion_decano(self, request, pk=None):
        """Facultad solicita al Decano que decida sobre la activación de una
        segunda instancia. No cambia 'activada': abre una Aprobacion
        pendiente."""
        aprobacion = SegundaInstanciaService.solicitar_activacion_decano(
            segunda_instancia_id=pk,
            usuario_revisor_id=request.data.get("usuario_revisor"),
            ejecutor=request.user,
            observacion=request.data.get("observacion"),
        )
        return Response(AprobacionSerializer(aprobacion).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=["post"],
        url_path="confirmar-activacion-decano/(?P<aprobacion_id>[^/.]+)",
    )
    def confirmar_activacion_decano(self, request, aprobacion_id=None):
        """El Decano confirma una solicitud abierta por Facultad: aprueba la
        Aprobacion y activa la segunda instancia."""
        instancia = SegundaInstanciaService.confirmar_activacion_decano(
            aprobacion_id=aprobacion_id,
            ejecutor=request.user,
            observacion_decano=request.data.get("observacion_decano"),
        )
        return Response(self.serializer_class(instancia).data)

    @action(
        detail=False, methods=["post"],
        url_path="denegar-activacion-decano/(?P<aprobacion_id>[^/.]+)",
    )
    def denegar_activacion_decano(self, request, aprobacion_id=None):
        """El Decano deniega una solicitud abierta por Facultad: rechaza la
        Aprobacion. La segunda instancia queda sin activar."""
        instancia = SegundaInstanciaService.denegar_activacion_decano(
            aprobacion_id=aprobacion_id,
            ejecutor=request.user,
            observacion=request.data.get("observacion"),
        )
        return Response(self.serializer_class(instancia).data)

    @action(detail=False, methods=["get"], url_path="activadas-pendientes")
    def activadas_pendientes(self, request):
        instancias = SegundaInstanciaService.listar_activadas_pendientes()
        return Response(self.serializer_class(instancias, many=True).data)