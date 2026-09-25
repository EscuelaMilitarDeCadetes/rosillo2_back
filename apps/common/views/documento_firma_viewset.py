from django.utils import timezone

from apps.common.models.documento_firma import DocumentoFirma
from apps.common.models.tipo_documento import TipoDocumento
from apps.common.pagination import CommonPageNumberPagination
from apps.usuarios.permissions.es_cexterno import EsCExterno
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_decano import EsDecano
from apps.usuarios.permissions.es_facultad import EsFacultad
from apps.usuarios.permissions.es_gerente import EsGerente
from apps.usuarios.permissions.es_grupo import EsGrupo
from apps.usuarios.permissions.es_supervisor import EsSupervisor
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from apps.common.serializers import DocumentoFirmaSerializer
from apps.common.services.documento_firma_service import DocumentoFirmaService
from django.http import FileResponse
import os

NOMBRES_TIPO_DOCUMENTO_CARGA_FACULTAD_GRUPO = {
    "Control de cambios",
    "Control de cambios - tiempo",
    "Control de cambios - investigador",
    "Control de cambios - costo",
    "Control de cambios - producto",
    "Entregables",
    "Informe técnico",
    "Informe de supervisión",
    "Concepto técnico",
    "Informe final",
}

def _resolver_objeto_generico(data):
    app_label = data.get("content_type_app_label")
    model = data.get("content_type_model")
    object_id = data.get("object_id")
    if not (app_label and model and object_id):
        return None
    content_type = ContentType.objects.get(app_label=app_label, model=model)
    return content_type.get_object_for_this_type(pk=object_id)


class DocumentoFirmaViewSet(viewsets.ViewSet):
    serializer_class = DocumentoFirmaSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_autoservicio = ['list', 'retrieve', 'por_tipo_documento', 'ultima_version', 'por_objeto', 'descargar', 'habilitados_para_firma']
        if self.action in acciones_autoservicio:
            permission_classes = [IsAuthenticated]
        elif self.action in ['marcar_rechazado', 'rechazar']:
            permission_classes = [EsDecano | EsSupervisor | EsGerente]
        else:  # create
            permission_classes = [EsFacultad | EsGrupo | EsCInterno | EsCExterno]
        return [permission() for permission in permission_classes]

    def list(self, request):
        documentos = DocumentoFirmaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(documentos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        documento = DocumentoFirmaService.obtener(pk)
        return Response(self.serializer_class(documento).data)

    def create(self, request):
        tipo_documento_id = request.data.get('tipo_documento')
        content_type_app_label = request.data.get('content_type_app_label')
        content_type_model = request.data.get('content_type_model')
        object_id = request.data.get('object_id')
        es_cinterno_cexterno = request.user.has_role('CINTERNO') or request.user.has_role('CEXTERNO')
        tipo = TipoDocumento.objects.filter(pk=tipo_documento_id).first()
        if not es_cinterno_cexterno:
            nombre_tipo = tipo.nombre_documento if tipo else None
            puede_cargar = tipo and (
                tipo.es_informe_seguimiento
                or nombre_tipo in NOMBRES_TIPO_DOCUMENTO_CARGA_FACULTAD_GRUPO
            )
            if not puede_cargar:
                return Response(
                    {"detail": "Con este rol no puede cargar este tipo de documento."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if content_type_app_label and content_type_model and object_id:
                content_type = ContentType.objects.get(app_label=content_type_app_label, model=content_type_model)
                tiene_acta = DocumentoFirma.objects.filter(
                    content_type=content_type, object_id=object_id, tipo_documento__es_acta_inicio=True,
                ).exists()
                if not tiene_acta:
                    return Response(
                        {"detail": "Aún no se puede cargar el documento: falta el acta de inicio."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if tipo.es_informe_seguimiento:
                    hoy = timezone.now()
                    ya_subido_este_mes = DocumentoFirma.objects.filter(
                        content_type=content_type, object_id=object_id,
                        tipo_documento__es_informe_seguimiento=True,
                        fecha_creacion__year=hoy.year,
                        fecha_creacion__month=hoy.month,
                    ).exists()
                    if ya_subido_este_mes:
                        return Response(
                            {"detail": "Ya se cargó el informe de seguimiento de este mes. Podrá cargar el siguiente el próximo mes."},
                            status=status.HTTP_403_FORBIDDEN,
                        )
        objeto = _resolver_objeto_generico(request.data)
        archivo = request.FILES.get("archivo")
        kwargs = dict(
            tipo_documento_id=request.data.get("tipo_documento"),
            ip_creacion=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            ejecutor=request.user,
            objeto=objeto,
            estado=request.data.get("estado", "BORRADOR"),
        )
        documento = (
            DocumentoFirmaService.crear_desde_archivo(archivo=archivo, **kwargs)
            if archivo is not None
            else DocumentoFirmaService.crear(ruta_documento=request.data.get("ruta_documento"), **kwargs)
        )
        if not es_cinterno_cexterno:
            DocumentoFirmaService.notificar_cinterno_carga(documento, ejecutor=request.user)
        return Response(self.serializer_class(documento).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        DocumentoFirmaService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="habilitar-para-firma")
    def habilitar_para_firma(self, request, pk=None):
        documento = DocumentoFirmaService.habilitar_para_firma(pk, ejecutor=request.user)
        return Response(self.serializer_class(documento).data)

    @action(detail=True, methods=["post"], url_path="marcar-rechazado")
    def marcar_rechazado(self, request, pk=None):
        documento = DocumentoFirmaService.marcar_rechazado(pk, ejecutor=request.user)
        return Response(self.serializer_class(documento).data)

    @action(detail=False, methods=["get"], url_path="por-tipo-documento")
    def por_tipo_documento(self, request):
        tipo_documento_id = request.query_params.get("tipo_documento")
        documentos = DocumentoFirmaService.listar_por_tipo_documento(tipo_documento_id)
        return Response(self.serializer_class(documentos, many=True).data)

    @action(detail=False, methods=["get"], url_path="ultima-version")
    def ultima_version(self, request):
        tipo_documento_id = request.query_params.get("tipo_documento")
        documento = DocumentoFirmaService.obtener_ultima_version(tipo_documento_id)
        if documento is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.serializer_class(documento).data)

    @action(detail=False, methods=["get"], url_path="habilitados-para-firma")
    def habilitados_para_firma(self, request):
        documentos = DocumentoFirmaService.listar_habilitados_para_firma()
        return Response(self.serializer_class(documentos, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-objeto")
    def por_objeto(self, request):
        objeto = _resolver_objeto_generico(request.query_params)
        if objeto is None:
            return Response(
                {"error": "Se requieren 'content_type_app_label', 'content_type_model' y 'object_id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        documentos = DocumentoFirmaService.listar_por_objeto(objeto)
        return Response(self.serializer_class(documentos, many=True).data)
    
    @action(detail=True, methods=["get"], url_path="descargar")
    def descargar(self, request, pk=None):
        documento = DocumentoFirmaService.obtener(pk)
        if not os.path.exists(documento.ruta_documento):
            return Response({"error": "El archivo no se encuentra en disco."}, status=status.HTTP_404_NOT_FOUND)
        nombre_archivo = os.path.basename(documento.ruta_documento)
        return FileResponse(open(documento.ruta_documento, "rb"), as_attachment=True, filename=nombre_archivo)