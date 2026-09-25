#apps/usuarios/views/rol_plataforma_viewset.py
from apps.usuarios.pagination import UsuariosPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..permissions.es_soporte import EsSoporte
from apps.usuarios.models import RolPlataforma
from apps.usuarios.serializers import RolPlataformaSerializer


class RolPlataformaViewSet(viewsets.ViewSet):
    queryset = RolPlataforma.objects.all()
    serializer_class = RolPlataformaSerializer
    pagination_class = UsuariosPageNumberPagination

    def get_permissions(self):
        permission_classes = [EsSoporte]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.queryset

    def list(self, request):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        rol = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(self.serializer_class(rol).data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # --- Permite a SOPORTE corregir nombre_rol/descripcion de un rol
    # existente. Solo vía PATCH (partial_update): el catálogo no admite
    # reemplazo total (PUT), únicamente corrección puntual de campos. No se
    # define update() a propósito, para que el router excluya PUT del mapeo
    # de verbos y responda 405, igual que hace con destroy(). ---
    def partial_update(self, request, pk=None):
        rol = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(rol, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)