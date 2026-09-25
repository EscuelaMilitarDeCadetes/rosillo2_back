from apps.common.pagination import CommonPageNumberPagination
from apps.usuarios.permissions.es_cexterno import EsCExterno
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_decano import EsDecano
from apps.usuarios.permissions.es_facultad import EsFacultad
from apps.usuarios.permissions.es_grupo import EsGrupo
from apps.usuarios.permissions.es_supervisor import EsSupervisor
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from apps.common.serializers import TareaSerializer
from apps.common.services.tarea_service import TareaService


class TareaViewSet(viewsets.ViewSet):
    serializer_class = TareaSerializer
    pagination_class = CommonPageNumberPagination

    def get_permissions(self):
        acciones_autoservicio = [
            'list', 'retrieve', 'por_usuario', 'por_objeto',
            'vencidas', 'proximas_a_vencer', 'completar',
        ]
        if self.action in acciones_autoservicio:
            permission_classes = [EsDecano | EsSupervisor | EsFacultad | EsGrupo | EsCInterno | EsCExterno]
        else:  # create, reasignar, destroy
            permission_classes = [EsFacultad | EsGrupo | EsCInterno | EsCExterno]
        return [permission() for permission in permission_classes]

    def list(self, request):
        tareas = TareaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tareas, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        tarea = TareaService.obtener(pk)
        return Response(self.serializer_class(tarea).data)

    def create(self, request):
        app_label = request.data.get("content_type_app_label")
        model = request.data.get("content_type_model")
        object_id = request.data.get("object_id")
        objeto = None
        if app_label and model and object_id:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            objeto = content_type.get_object_for_this_type(pk=object_id)
        tarea = TareaService.crear(
            asignado_a_id=request.user.pk,   # siempre el usuario autenticado
            descripcion=request.data.get("descripcion"),
            objeto=objeto,
            ejecutor=request.user,
            fecha_limite=request.data.get("fecha_limite"),
        )
        return Response(self.serializer_class(tarea).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        TareaService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def reasignar(self, request, pk=None):
        tarea = TareaService.reasignar(pk, request.data.get("asignado_a"), ejecutor=request.user)
        return Response(self.serializer_class(tarea).data)

    @action(detail=True, methods=["post"])
    def completar(self, request, pk=None):
        tarea = TareaService.obtener(pk)
        es_asignado = tarea.asignado_a_id == request.user.pk
        es_revisor = request.user.has_role('DECANO') or request.user.has_role('SUPERVISOR')
        if not (es_asignado or es_revisor):
            return Response(status=status.HTTP_403_FORBIDDEN)
        tarea = TareaService.completar(pk, ejecutor=request.user)
        return Response(self.serializer_class(tarea).data)

    @action(detail=False, methods=["get"], url_path="por-usuario/(?P<usuario_id>[^/.]+)")
    def por_usuario(self, request, usuario_id=None):
        roles_con_visibilidad_ampliada = ('SOPORTE', 'CINTERNO', 'FACULTAD', 'GRUPO', 'CEXTERNO')
        if str(request.user.pk) != str(usuario_id) and not any(
            request.user.has_role(r) for r in roles_con_visibilidad_ampliada
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)
        solo_pendientes = request.query_params.get("solo_pendientes", "false").lower() == "true"
        tareas = TareaService.listar_por_usuario(usuario_id, solo_pendientes=solo_pendientes)
        return Response(self.serializer_class(tareas, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-objeto")
    def por_objeto(self, request):
        content_type = ContentType.objects.get(
            app_label=request.query_params.get("content_type_app_label"),
            model=request.query_params.get("content_type_model"),
        )
        objeto = content_type.get_object_for_this_type(pk=request.query_params.get("object_id"))
        tareas = TareaService.listar_por_objeto(objeto)
        return Response(self.serializer_class(tareas, many=True).data)

    @action(detail=False, methods=["get"])
    def vencidas(self, request):
        tareas = TareaService.listar_vencidas()
        return Response(self.serializer_class(tareas, many=True).data)

    @action(detail=False, methods=["get"], url_path="proximas-a-vencer")
    def proximas_a_vencer(self, request):
        dias = int(request.query_params.get("dias", 3))
        tareas = TareaService.listar_proximas_a_vencer(dias=dias)
        return Response(self.serializer_class(tareas, many=True).data)