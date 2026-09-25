from apps.common.pagination import CommonPageNumberPagination
from apps.usuarios.permissions.es_cexterno import EsCExterno
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_facultad import EsFacultad
from apps.usuarios.permissions.es_grupo import EsGrupo
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.common.serializers import DocumentoFirmanteSerializer
from apps.common.services.documento_firmante_service import DocumentoFirmanteService


class DocumentoFirmanteViewSet(viewsets.ViewSet):
    serializer_class = DocumentoFirmanteSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_autoservicio = ['list', 'retrieve', 'firmar', 'rechazar', 'por_documento',
                        'pendientes_por_usuario', 'siguiente_turno']
        if self.action in acciones_autoservicio:
            permission_classes = [IsAuthenticated]
        else:  # create, destroy, asignar_varios, generar_codigo
            permission_classes = [EsFacultad | EsGrupo | EsCInterno | EsCExterno]
        return [permission() for permission in permission_classes]

    def list(self, request):
        firmantes = DocumentoFirmanteService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(firmantes, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        firmante = DocumentoFirmanteService.obtener(pk)
        return Response(self.serializer_class(firmante).data)

    def create(self, request):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=request.data.get("documento_firma"),
            usuario_id=request.data.get("usuario"),
            orden=request.data.get("orden"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(firmante).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        DocumentoFirmanteService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="asignar-varios")
    def asignar_varios(self, request):
        documento_firma_id = request.data.get("documento_firma")
        usuarios_ids = request.data.get("usuarios_ids", [])
        firmantes = DocumentoFirmanteService.asignar_firmantes(
            documento_firma_id, usuarios_ids, ejecutor=request.user
        )
        return Response(
            self.serializer_class(firmantes, many=True).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="generar-codigo")
    def generar_codigo(self, request, pk=None):
        firmante = DocumentoFirmanteService.generar_codigo_verificacion(pk, ejecutor=request.user)
        return Response({"message": "Código de verificación enviado."})

    @action(detail=True, methods=["post"])
    def firmar(self, request, pk=None):
        firmante = DocumentoFirmanteService.firmar(
            documento_firmante_id=pk,
            codigo_verificacion=request.data.get("codigo_verificacion"),
            ip_firma=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            ruta_firma=request.data.get("ruta_firma", ""),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(firmante).data)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        firmante = DocumentoFirmanteService.rechazar(
            documento_firmante_id=pk,
            motivo_rechazo=request.data.get("motivo_rechazo"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(firmante).data)

    @action(detail=False, methods=["get"], url_path="por-documento")
    def por_documento(self, request):
        documento_firma_id = request.query_params.get("documento_firma")
        firmantes = DocumentoFirmanteService.listar_por_documento(documento_firma_id)
        return Response(self.serializer_class(firmantes, many=True).data)

    @action(detail=False, methods=["get"], url_path="pendientes-por-usuario/(?P<usuario_id>[^/.]+)")
    def pendientes_por_usuario(self, request, usuario_id=None):
        roles_con_visibilidad_ampliada = ('SOPORTE', 'CINTERNO', 'FACULTAD', 'GRUPO', 'CEXTERNO')
        if str(request.user.pk) != str(usuario_id) and not any(
            request.user.has_role(r) for r in roles_con_visibilidad_ampliada
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)
        firmantes = DocumentoFirmanteService.listar_pendientes_por_usuario(usuario_id)
        return Response(self.serializer_class(firmantes, many=True).data)

    @action(detail=False, methods=["get"], url_path="siguiente-turno")
    def siguiente_turno(self, request):
        documento_firma_id = request.query_params.get("documento_firma")
        firmante = DocumentoFirmanteService.obtener_siguiente_turno(documento_firma_id)
        if firmante is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.serializer_class(firmante).data)