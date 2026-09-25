# apps/investigacion_formativa/views/banco_ideas_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.pagination import InvestigacionFormativaPageNumberPagination
from apps.investigacion_formativa.serializers.banco_ideas_serializer import BancoIdeasSerializer
from apps.investigacion_formativa.services.banco_ideas_service import BancoIdeasService
from apps.investigacion_formativa.permissions import (
    combinar,
    ROLES_LECTURA_INVESTIGACION_FORMATIVA,
    ROLES_ESCRITURA_GESTION,
    ROLES_INTERACCION_BANCO_IDEAS,
)


class BancoIdeasViewSet(viewsets.ViewSet):
    serializer_class = BancoIdeasSerializer
    pagination_class = InvestigacionFormativaPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            # Alta/edicion/borrado del catalogo de ideas: administrativo.
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormativa()]
        elif self.action in ["separar", "tomar", "liberar"]:
            # Tomar/liberar una idea es una accion del propio estudiante
            # (o de Facultad/Decano/Soporte gestionando en su nombre).
            return [combinar(ROLES_INTERACCION_BANCO_IDEAS), TieneAmbitoFormativa()]
        else:  # list, retrieve, por_facultad, disponibles
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    def list(self, request):
        ideas = BancoIdeasService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(ideas, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        idea = BancoIdeasService.obtener(pk)
        return Response(self.serializer_class(idea).data)

    def create(self, request):
        idea = BancoIdeasService.crear(
            facultad_id=request.data.get("facultad"),
            idea=request.data.get("idea"),
            descripcion=request.data.get("descripcion"),
            linea_investigacion=request.data.get("linea_investigacion"),
            palabras_clave=request.data.get("palabras_clave"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(idea).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        idea = BancoIdeasService.actualizar(
            idea_id=pk,
            descripcion=request.data.get("descripcion"),
            linea_investigacion=request.data.get("linea_investigacion"),
            palabras_clave=request.data.get("palabras_clave"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(idea).data)

    def destroy(self, request, pk=None):
        BancoIdeasService.eliminar(idea_id=pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-facultad/(?P<facultad_id>[^/.]+)")
    def por_facultad(self, request, facultad_id=None):
        estado = request.query_params.get("estado")
        ideas = BancoIdeasService.listar_por_facultad(facultad_id, estado=estado)
        return Response(self.serializer_class(ideas, many=True).data)

    @action(detail=False, methods=["get"], url_path="disponibles")
    def disponibles(self, request):
        facultad_id = request.query_params.get("facultad")
        ideas = BancoIdeasService.listar_disponibles(facultad_id=facultad_id)
        return Response(self.serializer_class(ideas, many=True).data)

    @action(detail=True, methods=["patch"], url_path="separar")
    def separar(self, request, pk=None):
        idea = BancoIdeasService.separar(idea_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(idea).data)

    @action(detail=True, methods=["patch"], url_path="tomar")
    def tomar(self, request, pk=None):
        idea = BancoIdeasService.tomar(idea_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(idea).data)

    @action(detail=True, methods=["patch"], url_path="liberar")
    def liberar(self, request, pk=None):
        idea = BancoIdeasService.liberar(idea_id=pk, ejecutor=request.user)
        return Response(self.serializer_class(idea).data)