from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formal.serializers.monto_serializer import MontoSerializer
from apps.investigacion_formal.services.monto_service import MontoService
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_ESCRITURA_GESTION, combinar,
)


class MontoViewSet(viewsets.ViewSet):
    serializer_class = MontoSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action in ["create", "asignar_aprobado", "asignar_contrapartida", "editar_valor_aprobado"]:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto, aprobados_calificados, contrapartida_calificados, totales_calificados, avance_presupuestal
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        montos = MontoService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(montos, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        monto = MontoService.obtener(pk)
        return Response(self.serializer_class(monto).data)

    def create(self, request):
        monto = MontoService.crear(
            proyecto_id=request.data.get("proyecto"),
            solicitado=request.data.get("solicitado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(monto).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="asignar-aprobado")
    def asignar_aprobado(self, request, pk=None):
        monto = MontoService.asignar_aprobado(
            monto_id=pk,
            aprobado=request.data.get("aprobado"),
            contrapartida=request.data.get("contrapartida"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(monto).data)

    @action(detail=True, methods=["patch"], url_path="editar-valor-aprobado")
    def editar_valor_aprobado(self, request, pk=None):
        monto = MontoService.editar_valor_aprobado(
            monto_id=pk,
            nuevo_aprobado=request.data.get("aprobado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(monto).data)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        monto = MontoService.obtener_por_proyecto(proyecto_id)
        if monto is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(self.serializer_class(monto).data)

    @action(detail=False, methods=["get"], url_path="aprobados-calificados")
    def aprobados_calificados(self, request):
        interno = request.query_params.get("interno", "true").lower() != "false"
        montos = MontoService.listar_aprobados_proyectos_calificados(interno=interno)
        return Response(self.serializer_class(montos, many=True).data)

    @action(detail=False, methods=["get"], url_path="contrapartida-calificados")
    def contrapartida_calificados(self, request):
        interno = request.query_params.get("interno", "true").lower() != "false"
        montos = MontoService.listar_contrapartida_proyectos_calificados(interno=interno)
        return Response(self.serializer_class(montos, many=True).data)

    @action(detail=False, methods=["get"], url_path="totales-calificados")
    def totales_calificados(self, request):
        interno = request.query_params.get("interno", "true").lower() != "false"
        montos = MontoService.listar_totales_proyectos_calificados(interno=interno)
        return Response(self.serializer_class(montos, many=True).data)
    
    @action(detail=False, methods=["get"], url_path="avance-presupuestal/(?P<proyecto_id>[^/.]+)")
    def avance_presupuestal(self, request, proyecto_id=None):
        """
        Widget aislado de % ejecutado. Para la ficha consolidada de
        seguimiento (avance + tiempo + presupuesto + objetivos) usar en
        cambio GET /proyectos/{id}/avance-ponderado/ (ProyectoViewSet).
        Ambos delegan en MontoService.calcular_avance_presupuestal().
        """
        avance = MontoService.calcular_avance_presupuestal(proyecto_id)
        return Response({"proyecto_id": int(proyecto_id), "avance_presupuestal": avance})
    
    @action(detail=True, methods=["patch"], url_path="asignar-contrapartida")
    def asignar_contrapartida(self, request, pk=None):
        monto = MontoService.asignar_contrapartida(
            monto_id=pk,
            contrapartida=request.data.get("contrapartida"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(monto).data)