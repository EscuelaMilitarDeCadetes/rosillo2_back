from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formal.serializers.convocatoria_serializer import ConvocatoriaSerializer
from apps.investigacion_formal.serializers.proyecto_x_convocatoria_serializer import (
    ProyectoXConvocatoriaSerializer,
)
from apps.investigacion_formal.services.convocatoria_service import ConvocatoriaService
from apps.investigacion_formal.services.proyecto_x_convocatoria_service import (
    ProyectoXConvocatoriaService,
)
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_CREACION_PROYECTO,
    ROLES_VEN_CONVOCATORIAS_ABIERTAS, combinar,
)
from apps.usuarios.permissions import EsAsesor, EsCInterno, TieneAmbitoFormal


class ConvocatoriaViewSet(viewsets.ViewSet):
    serializer_class = ConvocatoriaSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [EsAsesor]
        elif self.action == "cambiar_estado":
            permission_classes = [EsCInterno]
        elif self.action in ["list", "retrieve", "internas"]:
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]
        elif self.action == "participar":
            return [combinar(ROLES_CREACION_PROYECTO), TieneAmbitoFormal()]
        elif self.action == "abiertas":
            return [combinar(ROLES_VEN_CONVOCATORIAS_ABIERTAS), TieneAmbitoFormal()]
        else:  # internas
            permission_classes = [EsCInterno]
        return [permission() for permission in permission_classes] + [TieneAmbitoFormal()]

    def list(self, request):
        convocatorias = ConvocatoriaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(convocatorias, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        convocatoria = ConvocatoriaService.obtener(pk)
        return Response(self.serializer_class(convocatoria).data)

    def create(self, request):
        convocatoria = ConvocatoriaService.crear_con_documento(
            nombre_convocatoria=request.data.get("nombre_convocatoria"),
            anio_convocatoria=request.data.get("anio_convocatoria"),
            inicio=request.data.get("inicio"),
            cierre=request.data.get("cierre"),
            interno=True,  
            archivo=request.FILES.get("archivo"),
            ip_creacion=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(convocatoria).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="cambiar-estado")
    def cambiar_estado(self, request, pk=None):
        convocatoria = ConvocatoriaService.cambiar_estado(
            convocatoria_id=pk,
            nuevo_estado=request.data.get("estado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(convocatoria).data)

    @action(detail=False, methods=["get"], url_path="internas")
    def internas(self, request):
        estado = request.query_params.get("estado")
        estado = estado.lower() == "true" if estado is not None else None
        convocatorias = ConvocatoriaService.listar_internas(estado=estado)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(convocatorias, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="abiertas")
    def abiertas(self, request):
        """Convocatorias internas activas para la pantalla de inicio.
        Sin paginación: normalmente hay una o dos abiertas."""
        convocatorias = ConvocatoriaService.listar_abiertas()
        return Response(self.serializer_class(convocatorias, many=True).data)
    
    @action(detail=True, methods=["post"], url_path="participar")
    def participar(self, request, pk=None):
        """
        Réplica de POST /proyecto/participarConvocatoria (Thymeleaf).
        Crea el Proyecto + Monto + hasta 3 documentos + el vínculo
        ProyectoXConvocatoria + las Calificaciones iniciales, todo en una
        sola transacción atómica orquestada por
        ProyectoXConvocatoriaService.participar_convocatoria().
        """
        vinculo = ProyectoXConvocatoriaService.participar_convocatoria(
            convocatoria_id=pk,
            titulo=request.data.get("titulo"),
            alianza=self._parse_bool(request.data.get("alianza")),
            financiado=self._parse_bool(request.data.get("financiado")),
            unidad_ejecutora=request.data.get("unidad_ejecutora"),
            linea_investigacion=request.data.get("linea_investigacion"),
            valor_solicitado=request.data.get("valor_solicitado"),
            doc_proyecto=request.FILES.get("doc_proyecto"),
            doc_carta=request.FILES.get("doc_carta"),
            doc_alianza=request.FILES.get("doc_alianza"),
            ip_creacion=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            ejecutor=request.user,
        )
        return Response(
            ProyectoXConvocatoriaSerializer(vinculo).data,
            status=status.HTTP_201_CREATED,
        )