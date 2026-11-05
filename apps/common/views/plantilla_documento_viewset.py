from apps.common.pagination import CommonPageNumberPagination
from apps.common.ambito import investigacion_visible, SIN_AMBITO
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.usuarios.permissions.es_facultad import EsFacultad
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import FileResponse
import os
from apps.common.serializers import PlantillaDocumentoSerializer
from apps.common.services.plantilla_documento_service import PlantillaDocumentoService


class PlantillaDocumentoViewSet(viewsets.ViewSet):
    serializer_class = PlantillaDocumentoSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_autoservicio = ['list', 'retrieve', 'por_tipo_documento', 'descargar']
        if self.action in acciones_autoservicio:
            permission_classes = [IsAuthenticated]
        else:
            # FACULTAD gestiona plantillas sólo cuando entra por formativa.
            permission_classes = [EsSoporte | EsCInterno | (EsFacultad & TieneAmbitoFormativa)]
        return [permission() for permission in permission_classes]

    @staticmethod
    def _ambito(request):
        """Módulo de la sesión ('formal'/'formativa'), o None si el token no
        trae ámbito (en ese caso no se filtra, como antes)."""
        ambito = investigacion_visible(request)
        return None if ambito == SIN_AMBITO else ambito

    def list(self, request):
        # Sólo las plantillas de tipos de documento del módulo de la sesión.
        plantillas = PlantillaDocumentoService.listar(investigacion=self._ambito(request))
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(plantillas, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        plantilla = PlantillaDocumentoService.obtener(pk)
        return Response(self.serializer_class(plantilla).data)

    def create(self, request):
        plantilla = PlantillaDocumentoService.crear(
            tipo_documento_id=request.data.get("tipo_documento"),
            ruta_documento=request.data.get("ruta_documento"),
            ejecutor=request.user,
            investigacion=self._ambito(request),
        )
        return Response(self.serializer_class(plantilla).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        plantilla = PlantillaDocumentoService.actualizar(
            plantilla_id=pk,
            ejecutor=request.user,
            ruta_documento=request.data.get("ruta_documento"),
            investigacion=self._ambito(request),
        )
        return Response(self.serializer_class(plantilla).data)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        plantilla = PlantillaDocumentoService.desactivar(
            pk, ejecutor=request.user, investigacion=self._ambito(request)
        )
        return Response(self.serializer_class(plantilla).data)

    @action(detail=False, methods=["get"], url_path="por-tipo-documento")
    def por_tipo_documento(self, request):
        tipo_documento_id = request.query_params.get("tipo_documento")
        plantilla = PlantillaDocumentoService.obtener_por_tipo_documento(tipo_documento_id)
        if plantilla is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.serializer_class(plantilla).data)
    
    @action(detail=True, methods=["get"], url_path="descargar")
    def descargar(self, request, pk=None):
        plantilla = PlantillaDocumentoService.obtener(pk)
        ruta = plantilla.ruta_documento
        ruta_absoluta = ruta if os.path.isabs(ruta) else os.path.join(str(settings.DOCUMENTOS_ROOT), ruta)
        if not os.path.exists(ruta_absoluta):
            return Response({"error": "El archivo no se encuentra en disco."}, status=status.HTTP_404_NOT_FOUND)
        nombre_archivo = os.path.basename(plantilla.ruta_documento)
        return FileResponse(open(ruta_absoluta, "rb"), as_attachment=True, filename=nombre_archivo)