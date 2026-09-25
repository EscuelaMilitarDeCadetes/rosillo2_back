from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formal.serializers.proyecto_serializer import ProyectoSerializer
from apps.investigacion_formal.services.proyecto_service import ProyectoService
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_ESCRITURA_GESTION,
    ROLES_CREACION_PROYECTO, combinar,
)
from apps.usuarios.permissions import EsCExterno
from apps.investigacion_formal.services.avance_service import AvanceService
from apps.investigacion_formal.services.monto_service import MontoService
from apps.investigacion_formal.serializers.avance_serializer import AvanceProyectoSerializer


ACCIONES_SOLO_CINTERNO_CEXTERNO = [
    "update", "destroy", "asignar_timeline", "editar_fecha_cierre",
    "cambiar_estado_aprobado", "subir_a_gruplac", "registrar_acta_cierre",
]


class ProyectoViewSet(viewsets.ViewSet):
    serializer_class = ProyectoSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_CREACION_PROYECTO), TieneAmbitoFormal()]   # antes: [EsFacultad | EsGrupo] inline
        elif self.action == "crear_externo":
            return [EsCExterno()]
        elif self.action in ACCIONES_SOLO_CINTERNO_CEXTERNO:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormal()]
        else:
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        proyectos = ProyectoService.listar_activos()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(proyectos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        proyecto = ProyectoService.obtener(pk)
        return Response(self.serializer_class(proyecto).data)

    def create(self, request):
        proyecto = ProyectoService.crear(
            usuario_id=request.data.get("usuario"),
            gerente_id=request.data.get("gerente"),
            titulo=request.data.get("titulo"),
            interno=request.data.get("interno"),
            alianza=request.data.get("alianza"),
            financiado=request.data.get("financiado"),
            unidad_ejecutora=request.data.get("unidad_ejecutora"),
            linea_investigacion=request.data.get("linea_investigacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(proyecto).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        proyecto = ProyectoService.actualizar(
            proyecto_id=pk,
            titulo=request.data.get("titulo"),
            unidad_ejecutora=request.data.get("unidad_ejecutora"),
            linea_investigacion=request.data.get("linea_investigacion"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(proyecto).data)

    def destroy(self, request, pk=None):
        ProyectoService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="asignar-timeline")
    def asignar_timeline(self, request, pk=None):
        proyecto = ProyectoService.asignar_timeline(
            proyecto_id=pk,
            fecha_inicio=request.data.get("fecha_inicio"),
            fecha_fin=request.data.get("fecha_fin"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(proyecto).data)

    @action(detail=True, methods=["patch"], url_path="editar-fecha-cierre")
    def editar_fecha_cierre(self, request, pk=None):
        proyecto = ProyectoService.editar_fecha_cierre(
            proyecto_id=pk,
            nueva_fecha_fin=request.data.get("fecha_fin"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(proyecto).data)

    @action(detail=True, methods=["patch"], url_path="cambiar-estado-aprobado")
    def cambiar_estado_aprobado(self, request, pk=None):
        proyecto = ProyectoService.cambiar_estado_aprobado(
            proyecto_id=pk,
            nuevo_estado_aprobado=request.data.get("estado_aprobado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(proyecto).data)

    @action(detail=True, methods=["patch"], url_path="subir-gruplac")
    def subir_a_gruplac(self, request, pk=None):
        proyecto = ProyectoService.subir_a_gruplac(pk, ejecutor=request.user)
        return Response(self.serializer_class(proyecto).data)

    @action(detail=True, methods=["patch"], url_path="registrar-acta-cierre")
    def registrar_acta_cierre(self, request, pk=None):
        proyecto = ProyectoService.registrar_acta_cierre(pk, ejecutor=request.user)
        return Response(self.serializer_class(proyecto).data)

    @action(detail=False, methods=["get"], url_path="por-estado-aprobado")
    def por_estado_aprobado(self, request):
        estado_aprobado = request.query_params.get("estado_aprobado")
        proyectos = ProyectoService.listar_por_estado_aprobado(estado_aprobado)
        return Response(self.serializer_class(proyectos, many=True).data)
    
    @action(detail=True, methods=["get"], url_path="avance-ponderado")
    def avance_ponderado(self, request, pk=None):
        """
        Ficha consolidada de seguimiento mensual (avance por objetivos +
        avance en tiempo + avance presupuestal). Para un widget aislado de
        solo presupuesto, usar en cambio
        GET /montos/avance-presupuestal/{proyecto_id}/ (MontoViewSet).
        """
        detalle = AvanceService.calcular_detalle_por_objetivo(pk)
        avance_objetivos = AvanceService.calcular_avance_ponderado(pk)
        avance_tiempo = AvanceService.calcular_avance_tiempo(pk)
        avance_presupuestal = MontoService.calcular_avance_presupuestal(pk)
        payload = {
            "proyecto_id": int(pk),
            "avance_ponderado": avance_objetivos,
            "avance_tiempo": avance_tiempo,
            "avance_presupuestal": avance_presupuestal,
            "detalle_por_objetivo": detalle,
        }
        return Response(AvanceProyectoSerializer(payload).data)
    
    @action(detail=False, methods=["post"], url_path="crear-externo")
    def crear_externo(self, request):
        proyecto = ProyectoService.crear_proyecto_externo(
            usuario_id=request.data.get("usuario"),
            gerente_id=request.data.get("gerente"),
            titulo=request.data.get("titulo"),
            unidad_ejecutora=request.data.get("unidad_ejecutora"),
            linea_investigacion=request.data.get("linea_investigacion"),
            entidad=request.data.get("entidad"),
            valor_solicitado=request.data.get("valor_solicitado"),
            alianza=request.data.get("alianza"),
            financiado=request.data.get("financiado"),
            grupo_investigacion_id=request.data.get("grupo_investigacion"),
            facultad_id=request.data.get("facultad"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(proyecto).data, status=status.HTTP_201_CREATED)