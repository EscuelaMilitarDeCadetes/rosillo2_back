from apps.institucional.pagination import InstitucionalPageNumberPagination
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.institucional.serializers import GradoEstudiosSerializer
from apps.usuarios.permissions.es_soporte import EsSoporte
from apps.institucional.services.grado_estudios_service import GradoEstudiosService


class GradoEstudiosViewSet(viewsets.ViewSet):
    serializer_class = GradoEstudiosSerializer
    pagination_class = InstitucionalPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def list(self, request):
        grados = GradoEstudiosService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(grados, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        grado = GradoEstudiosService.obtener(pk)
        serializer = self.serializer_class(grado)
        return Response(serializer.data)

    def create(self, request):
        grado = GradoEstudiosService.crear(
            sigla_grado=request.data.get("sigla_grado"),
            descripcion=request.data.get("descripcion"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(grado)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        grado = GradoEstudiosService.actualizar(
            grado_id=pk,
            sigla_grado=request.data.get("sigla_grado"),
            descripcion=request.data.get("descripcion"),
            ejecutor=request.user,
        )
        serializer = self.serializer_class(grado)
        return Response(serializer.data)