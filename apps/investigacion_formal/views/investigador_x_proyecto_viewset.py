from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formal.serializers.investigador_x_proyecto_serializer import (
    InvestigadorXProyectoSerializer,
)
from apps.investigacion_formal.services.investigador_x_proyecto_service import (
    InvestigadorXProyectoService,
)
from apps.investigacion_formal.services.investigador_completo_service import (
    InvestigadorCompletoService,
)
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_ESCRITURA_GESTION, ROLES_CREACION_OPERATIVA, ProyectoTieneActaInicio, combinar,
)
from apps.usuarios.permissions import TieneAmbitoFormal


class InvestigadorXProyectoViewSet(viewsets.ViewSet):
    serializer_class = InvestigadorXProyectoSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "registrar_completo"]:
            return [combinar(ROLES_CREACION_OPERATIVA), TieneAmbitoFormal(), ProyectoTieneActaInicio()]
        elif self.action in ["update", "destroy"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        investigadores = InvestigadorXProyectoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(investigadores, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        investigador = InvestigadorXProyectoService.obtener(pk)
        return Response(self.serializer_class(investigador).data)

    def create(self, request):
        investigador = InvestigadorXProyectoService.crear(
            rol_investigador_id=request.data.get("rol_investigador"),
            proyecto_id=request.data.get("proyecto"),
            persona_x_grupo_id=request.data.get("persona_x_grupo"),
            ejecutor=request.user,
            orcid=request.data.get("orcid"),
        )
        return Response(self.serializer_class(investigador).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        investigador = InvestigadorXProyectoService.actualizar(
            investigador_x_proyecto_id=pk,
            ejecutor=request.user,
            rol_investigador_id=request.data.get("rol_investigador"),
            orcid=request.data.get("orcid"),
        )
        return Response(self.serializer_class(investigador).data)

    def destroy(self, request, pk=None):
        InvestigadorXProyectoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        solo_activos = request.query_params.get("solo_activos", "true").lower() != "false"
        investigadores = InvestigadorXProyectoService.listar_por_proyecto(
            proyecto_id, solo_activos=solo_activos
        )
        return Response(self.serializer_class(investigadores, many=True).data)

    @action(detail=False, methods=["post"], url_path="registrar-completo")
    def registrar_completo(self, request):
        """
        Réplica de InvestigadorXproyectoControlador.newInvestigadorFull()
        (Thymeleaf). Registra una Persona nueva, la vincula a un Grupo de
        Investigación (PersonaXGrupo) y la asigna al Proyecto como
        investigador (InvestigadorXProyecto), todo en una sola transacción
        atómica vía InvestigadorCompletoService.

        Mismo permiso que create() (ROLES_CREACION_OPERATIVA): existe
        justamente para que CINTERNO/CEXTERNO/FACULTAD/GRUPO puedan dar de
        alta un investigador nuevo sin depender de EsSoporte, que es lo que
        exige crear una Persona directamente vía PersonaViewSet.
        """
        investigador = InvestigadorCompletoService.registrar_completo(
            grado_id=request.data.get("grado"),
            nombre=request.data.get("nombre"),
            apellido=request.data.get("apellido"),
            documento=request.data.get("documento"),
            celular=request.data.get("celular"),
            correo=request.data.get("correo"),
            cvlac=request.data.get("cvlac"),
            grupo_id=request.data.get("grupo"),
            rol_grupo_id=request.data.get("rol_grupo"),
            proyecto_id=request.data.get("proyecto"),
            rol_investigador_id=request.data.get("rol_investigador"),
            orcid=request.data.get("orcid"),
            vinculacion=request.data.get("vinculacion"),
            ejecutor=request.user,
        )
        return Response(
            self.serializer_class(investigador).data, status=status.HTTP_201_CREATED
        )