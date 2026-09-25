from apps.institucional.pagination import InstitucionalPageNumberPagination
from apps.usuarios.permissions.es_decano import EsDecano
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.institucional.serializers import PersonaXGrupoSerializer
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.usuarios.permissions.es_supervisor import EsSupervisor
from apps.usuarios.permissions.es_asesor import EsAsesor
from apps.usuarios.permissions.es_facultad import EsFacultad
from apps.usuarios.permissions.es_grupo import EsGrupo
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_cexterno import EsCExterno
from apps.institucional.services.persona_x_grupo_service import PersonaXGrupoService


class PersonaXGrupoViewSet(viewsets.ViewSet):
    """
    Adaptador HTTP puro: toda la lógica vive en PersonaXGrupoService.

    DELETE /persona-grupo/{id}/ -> eliminar() = SOFT-DELETE (desvincula,
    pone estado=False y registra fecha de desvinculación).
    POST   /persona-grupo/{id}/reactivar/ -> revierte la desvinculación.
    GET    /persona-grupo/con-grupo/ -> listar_con_grupo().
    GET    /persona-grupo/por-persona/{persona_id}/ -> listar_por_persona().
    """
    serializer_class = PersonaXGrupoSerializer
    pagination_class = InstitucionalPageNumberPagination

    _acciones_lectura = [
        'list', 'retrieve', 'con_grupo', 'por_persona',
        'historial_persona', 'activas', 'facultad', 'grupo', 'tipo',
    ]

    def get_permissions(self):
        if self.action in self._acciones_lectura:
            permission_classes = [
                EsSoporte | EsSupervisor | EsAsesor | EsFacultad | EsGrupo | EsCInterno | EsCExterno | EsDecano
            ]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        vinculos = PersonaXGrupoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(vinculos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        vinculo = PersonaXGrupoService.obtener(pk)
        serializer = self.serializer_class(vinculo)
        return Response(serializer.data)

    def create(self, request):
        vinculo = PersonaXGrupoService.crear(
            persona_id=request.data.get("persona"),
            rol_grupo_id=request.data.get("rol_grupo"),
            grupo_id=request.data.get("grupo"),
            facultad_id=request.data.get("facultad"),
            vinculacion=request.data.get("vinculacion"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(vinculo)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        vinculo = PersonaXGrupoService.actualizar(
            persona_x_grupo_id=pk,
            ejecutor=request.user,
            rol_grupo_id=request.data.get("rol_grupo"),
            grupo_id=request.data.get("grupo"),
            facultad_id=request.data.get("facultad"),
            vinculacion=request.data.get("vinculacion"),
        )
        serializer = self.serializer_class(vinculo)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        PersonaXGrupoService.eliminar(
            pk,
            ejecutor=request.user,
            desvinculacion=request.data.get("desvinculacion"),
        )
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def reactivar(self, request, pk=None):
        vinculo = PersonaXGrupoService.reactivar(pk, ejecutor=request.user)
        serializer = self.serializer_class(vinculo)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="trasladar-grupo")
    def trasladar_grupo(self, request, pk=None):
        nuevo_grupo_id = request.data.get("nuevo_grupo_id")
        if not nuevo_grupo_id:
            return Response(
                {"error": "El campo 'nuevo_grupo_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            vinculo = PersonaXGrupoService.trasladar_a_grupo(
                persona_x_grupo_id=pk,
                nuevo_grupo_id=nuevo_grupo_id,
                ejecutor=request.user,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(vinculo)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="trasladar-facultad")
    def trasladar_facultad(self, request, pk=None):
        nueva_facultad_id = request.data.get("nueva_facultad_id")
        if not nueva_facultad_id:
            return Response(
                {"error": "El campo 'nueva_facultad_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            vinculo = PersonaXGrupoService.trasladar_a_facultad(
                persona_x_grupo_id=pk,
                nueva_facultad_id=nueva_facultad_id,
                ejecutor=request.user,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(vinculo)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="cambiar-rol")
    def cambiar_rol(self, request, pk=None):
        nuevo_rol_grupo_id = request.data.get("nuevo_rol_grupo_id")
        if not nuevo_rol_grupo_id:
            return Response(
                {"error": "El campo 'nuevo_rol_grupo_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            vinculo = PersonaXGrupoService.cambiar_rol(
                persona_x_grupo_id=pk,
                nuevo_rol_grupo_id=nuevo_rol_grupo_id,
                ejecutor=request.user,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(vinculo)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="con-grupo")
    def con_grupo(self, request):
        excluir_rol_grupo_id = request.query_params.get("excluir_rol_grupo_id")
        excluir_rol_grupo_id = int(excluir_rol_grupo_id) if excluir_rol_grupo_id else None
        vinculos = PersonaXGrupoService.listar_con_grupo(excluir_rol_grupo_id=excluir_rol_grupo_id)
        serializer = self.serializer_class(vinculos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-persona/(?P<persona_id>[^/.]+)")
    def por_persona(self, request, persona_id=None):
        solo_activos = request.query_params.get("solo_activos", "true").lower() != "false"
        vinculos = PersonaXGrupoService.listar_por_persona(persona_id, solo_activos=solo_activos)
        serializer = self.serializer_class(vinculos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path=r"persona/(?P<persona_id>[^/.]+)")
    def historial_persona(self, request, persona_id=None):
        registros = PersonaXGrupoService.historial_persona(persona_id)
        serializer = self.serializer_class(registros, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path=r"persona/(?P<persona_id>[^/.]+)/activas")
    def activas(self, request, persona_id=None):
        registros = PersonaXGrupoService.listar_activas_persona(persona_id)
        serializer = self.serializer_class(registros, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path=r"persona/(?P<persona_id>[^/.]+)/facultad")
    def facultad(self, request, persona_id=None):
        facultad = PersonaXGrupoService.obtener_facultad_activa(persona_id)
        if facultad is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"id": facultad.id, "nombre": facultad.nombre_facultad, "abreviatura": facultad.abreviatura})

    @action(detail=False, methods=["get"], url_path=r"persona/(?P<persona_id>[^/.]+)/grupo")
    def grupo(self, request, persona_id=None):
        grupo = PersonaXGrupoService.obtener_grupo_activo(persona_id)
        if grupo is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"id": grupo.id, "nombre": grupo.nombre_grupo, "sigla": grupo.sigla_grupo})

    @action(detail=False, methods=["get"], url_path=r"persona/(?P<persona_id>[^/.]+)/tipo")
    def tipo(self, request, persona_id=None):
        if PersonaXGrupoService.es_administrativo(persona_id):
            return Response({"tipo": "ADMINISTRATIVO"})
        if PersonaXGrupoService.pertenece_a_grupo(persona_id):
            return Response({"tipo": "INVESTIGADOR"})
        return Response({"tipo": "FACULTAD"})