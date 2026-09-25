from apps.usuarios.models.usuario_x_persona import UsuarioXPersona
from apps.usuarios.pagination import UsuariosPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ..serializers.usuario_serializer import UsuarioSerializer
from apps.usuarios.services.usuario_facade import UsuarioFacade
from rest_framework.exceptions import PermissionDenied
from django.db.models import Prefetch, Q

from ..permissions.es_soporte import EsSoporte
from ..permissions.es_asesor import EsAsesor
from ..permissions.es_facultad import EsFacultad
from ..permissions.es_grupo import EsGrupo
from ..permissions.es_cinterno import EsCInterno
from ..permissions.es_cexterno import EsCExterno
from ..permissions.es_decano import EsDecano
from ..permissions.es_supervisor import EsSupervisor

User = get_user_model()


class UsuarioViewSet(viewsets.ViewSet):
    """
    Las acciones de 'desactivar' y 'activar' delegan la lógica al UsuarioFacade.
    """
    serializer_class = UsuarioSerializer
    pagination_class = UsuariosPageNumberPagination

    def get_permissions(self):
        if self.action in ('desactivar_usuario', 'activar_usuario'):
            # Acciones sensibles: solo SOPORTE puede desactivar/activar usuarios.
            permission_classes = [EsSoporte]
        elif self.action == 'creados_por_mi':
            permission_classes = [EsFacultad | EsSoporte]
        elif self.action == 'buscar':
            permission_classes = [
                EsSoporte | EsAsesor | EsFacultad | EsSupervisor |
                EsGrupo | EsCInterno | EsCExterno | EsDecano
            ]
        else:
            permission_classes = [
                EsSoporte | EsAsesor | EsFacultad | EsSupervisor |
                EsGrupo | EsCInterno | EsCExterno | EsDecano
            ]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return (
            User.objects.filter(is_staff=False)
            .order_by('id')
            .prefetch_related(
                Prefetch("asignaciones", queryset=UsuarioXPersona.objects.filter(estado=True).select_related("persona"))
            )
        )

    def list(self, request):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        usuario = get_object_or_404(self.get_queryset(), pk=pk)
        return Response(self.serializer_class(usuario).data)

    @action(detail=True, methods=['post'], url_path='desactivar')
    def desactivar_usuario(self, request, pk=None):
        try:
            UsuarioFacade.service().desactivar_usuario(pk, ejecutor=request.user)
            return Response({"message": "Usuario desactivado correctamente."})
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='activar')
    def activar_usuario(self, request, pk=None):
        try:
            UsuarioFacade.service().activar_usuario(pk, ejecutor=request.user)
            return Response({"message": "Usuario activado correctamente."})
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'], url_path='creados-por-mi')
    def creados_por_mi(self, request):
        """Usuarios (activos e inactivos) creados por el ejecutor. Le permite
        a Facultad encontrar un tutor/jurado que ya tiene cuenta (aunque esté
        desactivada de un proceso anterior) y reactivarla en vez de duplicarla."""
        usuarios = UsuarioFacade.service().listar_creados_por(request.user)
        return Response(self.serializer_class(usuarios, many=True).data)

    @action(detail=False, methods=['get'], url_path='inactivos')
    def usuarios_inactivos(self, request):
        usuarios = self.get_queryset().filter(is_active=False)
        return Response(self.serializer_class(usuarios, many=True).data)

    @action(detail=False, methods=['get'], url_path='admin-dashboard')
    def dashboard(self, request):
        from apps.usuarios.models import RolPlataforma
        from apps.usuarios.serializers import RolPlataformaSerializer
        todos = list(self.get_queryset().order_by('id'))
        activos = [u for u in todos if u.is_active]
        inactivos = [u for u in todos if not u.is_active]
        return Response({
            "usuarios_activos": self.serializer_class(activos, many=True).data,
            "usuarios_inactivos": self.serializer_class(inactivos, many=True).data,
            "roles_disponibles": RolPlataformaSerializer(RolPlataforma.objects.all(), many=True).data,
        })

    @action(detail=True, methods=['get'], url_path='roles-activos')
    def roles_activos(self, request, pk=None):
        from apps.usuarios.services.rol_x_usuario_service import RolXUsuarioService
        from apps.usuarios.serializers import RolXUsuarioSerializer
        roles = RolXUsuarioService.listar_roles_de_usuario(usuario_id=pk)
        return Response(RolXUsuarioSerializer(roles, many=True).data)
    
    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        q = request.query_params.get('q', '').strip()
        queryset = self.get_queryset()
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(email__icontains=q)
                | Q(asignaciones__persona__nombre__icontains=q, asignaciones__estado=True)
                | Q(asignaciones__persona__apellido__icontains=q, asignaciones__estado=True)
                | Q(asignaciones__persona__documento__icontains=q, asignaciones__estado=True)
            ).distinct()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)