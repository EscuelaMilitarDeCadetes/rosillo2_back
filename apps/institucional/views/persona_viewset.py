from apps.institucional.pagination import InstitucionalPageNumberPagination
from apps.usuarios.permissions.es_decano import EsDecano
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.institucional.serializers import PersonaSerializer
from apps.institucional.services.persona_service import PersonaService
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.usuarios.permissions.es_supervisor import EsSupervisor
from apps.usuarios.permissions.es_asesor import EsAsesor
from apps.usuarios.permissions.es_facultad import EsFacultad
from apps.usuarios.permissions.es_grupo import EsGrupo
from apps.usuarios.permissions.es_cinterno import EsCInterno
from apps.usuarios.permissions.es_cexterno import EsCExterno


class PersonaViewSet(viewsets.ViewSet):
    serializer_class = PersonaSerializer
    pagination_class = InstitucionalPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'buscar']:
            permission_classes = [
                EsSoporte | EsSupervisor | EsAsesor | EsFacultad | EsGrupo | EsCInterno | EsCExterno | EsDecano
            ]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        personas = PersonaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(personas, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        persona = PersonaService.obtener(pk)
        serializer = self.serializer_class(persona)
        return Response(serializer.data)

    def create(self, request):
        persona = PersonaService.crear(
            grado_id=request.data.get("grado"),
            nombre=request.data.get("nombre"),
            apellido=request.data.get("apellido"),
            documento=request.data.get("documento"),
            celular=request.data.get("celular"),
            correo=request.data.get("correo"),
            cvlac=request.data.get("cvlac"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(persona)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        persona = PersonaService.actualizar(
            persona_id=pk,
            ejecutor=request.user,
            grado_id=request.data.get("grado"),
            nombre=request.data.get("nombre"),
            apellido=request.data.get("apellido"),
            documento=request.data.get("documento"),
            celular=request.data.get("celular"),
            correo=request.data.get("correo"),
            cvlac=request.data.get("cvlac"),
        )
        serializer = self.serializer_class(persona)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="buscar")
    def buscar(self, request):
        """
        Selector paginado y filtrado de Persona, pensado para dropdowns
        con búsqueda server-side  donde no es seguro asumir que toda la 
        base de Personas cabe en una sola página cargada de antemano en 
        el frontend. Sin 'q' (o vacío) se comporta igual que list(), 
        solo que bajo una URL dedicada para no mezclar semánticas en el 
        mismo thunk.
        """
        texto = request.query_params.get("q", "").strip()
        personas = PersonaService.listar_filtrado(texto or None)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(personas, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)