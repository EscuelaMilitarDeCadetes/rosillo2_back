# apps/investigacion_formal/views/proyecto_x_convocatoria_viewset.py
from apps.investigacion_formal.models.convocatoria import Convocatoria
from apps.investigacion_formal.pagination import InvestigacionFormalPageNumberPagination
from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.investigacion_formal.serializers.proyecto_x_convocatoria_serializer import (
    ProyectoXConvocatoriaSerializer,
)
from apps.investigacion_formal.services.proyecto_x_convocatoria_service import (
    ProyectoXConvocatoriaService,
)
from apps.investigacion_formal.permissions import (
    ROLES_LECTURA_INVESTIGACION_FORMAL, ROLES_ESCRITURA_GESTION,
    ROLES_CREACION_PROYECTO, combinar,
)
from django.http import HttpResponse
from apps.investigacion_formal.services.exportacion_service import ExportacionService
from apps.investigacion_formal.selectors.proyecto_x_convocatoria_selector import (
    ProyectoXConvocatoriaSelector,
)
from apps.investigacion_formal.selectors.convocatoria_selector import ConvocatoriaSelector

ACCIONES_SOLO_CINTERNO_CEXTERNO = [
    "destroy", "habilitar_correccion", "deshabilitar_correccion", "finalizar_calificacion",
]


class ProyectoXConvocatoriaViewSet(viewsets.ViewSet):
    serializer_class = ProyectoXConvocatoriaSerializer
    pagination_class = InvestigacionFormalPageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            return [combinar(ROLES_CREACION_PROYECTO), TieneAmbitoFormal()]   # antes: [EsFacultad | EsGrupo] inline
        elif self.action in ACCIONES_SOLO_CINTERNO_CEXTERNO:
            return [combinar(ROLES_ESCRITURA_GESTION), TieneAmbitoFormal()]
        else:  # list, retrieve, por_proyecto, por_convocatoria, sin_calificar, calificados, por_facultad, por_grupos
            return [combinar(ROLES_LECTURA_INVESTIGACION_FORMAL), TieneAmbitoFormal()]

    def list(self, request):
        registros = ProyectoXConvocatoriaService.listar()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        registro = ProyectoXConvocatoriaService.obtener(pk)
        return Response(self.serializer_class(registro).data)

    def create(self, request):
        registro = ProyectoXConvocatoriaService.crear(
            convocatoria_id=request.data.get("convocatoria"),
            proyecto_id=request.data.get("proyecto"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(registro).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        ProyectoXConvocatoriaService.eliminar(pk, ejecutor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="habilitar-correccion")
    def habilitar_correccion(self, request, pk=None):
        registro = ProyectoXConvocatoriaService.habilitar_correccion(pk, ejecutor=request.user)
        return Response(self.serializer_class(registro).data)

    @action(detail=True, methods=["patch"], url_path="deshabilitar-correccion")
    def deshabilitar_correccion(self, request, pk=None):
        registro = ProyectoXConvocatoriaService.deshabilitar_correccion(pk, ejecutor=request.user)
        return Response(self.serializer_class(registro).data)

    @action(detail=True, methods=["patch"], url_path="finalizar-calificacion")
    def finalizar_calificacion(self, request, pk=None):
        registro = ProyectoXConvocatoriaService.finalizar_calificacion(
            proyecto_x_convocatoria_id=pk,
            aprobado=request.data.get("aprobado"),
            ejecutor=request.user,
        )
        return Response(self.serializer_class(registro).data)

    @action(detail=False, methods=["get"], url_path="por-proyecto/(?P<proyecto_id>[^/.]+)")
    def por_proyecto(self, request, proyecto_id=None):
        registros = ProyectoXConvocatoriaService.listar_por_proyecto(proyecto_id)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-convocatoria/(?P<convocatoria_id>[^/.]+)")
    def por_convocatoria(self, request, convocatoria_id=None):
        registros = ProyectoXConvocatoriaService.listar_por_convocatoria(convocatoria_id)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="sin-calificar")
    def sin_calificar(self, request):
        registros = ProyectoXConvocatoriaService.listar_sin_calificar()
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="calificados")
    def calificados(self, request):
        calificacion = request.query_params.get("calificacion")
        registros = ProyectoXConvocatoriaService.listar_calificados(calificacion=calificacion)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-facultad/(?P<facultad_id>[^/.]+)")
    def por_facultad(self, request, facultad_id=None):
        registros = ProyectoXConvocatoriaService.listar_por_facultad(facultad_id)
        return Response(self.serializer_class(registros, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-grupo/(?P<grupo_id>[^/.]+)")
    def por_grupo(self, request, grupo_id=None):
        registros = ProyectoXConvocatoriaService.listar_por_grupo(grupo_id)
        return Response(self.serializer_class(registros, many=True).data)
    
    @action(detail=False, methods=["get"], url_path="buscar")
    def buscar(self, request):
        filtros = dict(
            convocatoria=request.query_params.get("convocatoria"),
            codigo=request.query_params.get("codigo"),
            titulo=request.query_params.get("titulo"),
            financiado=self._parse_bool(request.query_params.get("financiado")),
            alianza=self._parse_bool(request.query_params.get("alianza")),
            responsable=request.query_params.get("responsable"),
            calificacion=request.query_params.get("calificacion"),
            anio_inicio=request.query_params.get("anio_inicio"),
            anio_fin=request.query_params.get("anio_fin"),
            interno=self._parse_bool(request.query_params.get("interno")),
            gruplac=self._parse_bool(request.query_params.get("gruplac")),
            estado=self._parse_bool(request.query_params.get("estado")),
            facultad_id=request.query_params.get("facultad_id"),
            grupo_id=request.query_params.get("grupo_id"),
            estado_finalizado_calificacion=self._parse_bool(
                request.query_params.get("estado_finalizado_calificacion")
            ),
            anio_convocatoria=request.query_params.get("anio_convocatoria"),
        )
        registros = ProyectoXConvocatoriaService.buscar_con_filtros(**filtros)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(registros, request, view=self)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def _filtros_desde_query_params(self, request):
        """Mismos parámetros de buscar_con_filtros (Hallazgo C), vía querystring."""
        qp = request.query_params
        return dict(
            convocatoria=qp.get("convocatoria"),
            codigo=qp.get("codigo"),
            titulo=qp.get("titulo"),
            financiado=(qp.get("financiado") == "true") if "financiado" in qp else None,
            alianza=(qp.get("alianza") == "true") if "alianza" in qp else None,
            responsable=qp.get("responsable"),
            calificacion=qp.get("calificacion"),
            anio_inicio=qp.get("anio_inicio"),
            anio_fin=qp.get("anio_fin"),
            interno=(qp.get("interno") == "true") if "interno" in qp else None,
            gruplac=(qp.get("gruplac") == "true") if "gruplac" in qp else None,
            estado=qp.get("estado"),
        )

    @action(detail=False, methods=["get"], url_path="export/excel")
    def export_excel(self, request):
        filtros = self._filtros_desde_query_params(request)
        queryset = ProyectoXConvocatoriaSelector.buscar_con_filtros(**filtros)
        buffer = ExportacionService.exportar_excel(queryset)
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=proyectos.xlsx"
        return response

    @action(detail=False, methods=["get"], url_path="export/pdf")
    def export_pdf(self, request):
        filtros = self._filtros_desde_query_params(request)
        queryset = ProyectoXConvocatoriaSelector.buscar_con_filtros(**filtros)
        buffer = ExportacionService.exportar_pdf(queryset)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=proyectos.pdf"
        return response
    
    @action(detail=False, methods=["get"], url_path="mis-proyectos")
    def mis_proyectos(self, request):
        registros = ProyectoXConvocatoriaService.listar_por_usuario(request.user.id)
        serializer = self.serializer_class(registros, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="opciones-filtro")
    def opciones_filtro(self, request):
        """
        Alimenta los dropdowns de filtro del frontend.
         Comportamiento dual, según si viene o no el query param `interno`:
         - SIN `interno` (uso de segProyectos.html / SegProyectosTable.js):
          listas SIN filtrar, igual que antes — este módulo muestra proyectos
          internos y externos mezclados, con su propio filtro "Tipo de
          convocatoria" aparte. Réplica de
          ConvocatoriaInternaServicio.getAllConvocatoria() +
          ProyectoServicio.findDistinctAniosInicio()/findDistinctAniosFin().
 
        - CON `interno=true|false` (uso de adminProyectosExternos.html /
          proyectosAprobados.html / proyectosRechazados.html vía
          ProjectsListPage.js): listas filtradas a convocatorias/años que
          efectivamente tienen proyectos calificados (estado_finalizado_
          calificacion=True) y aprobados del tipo solicitado. Réplica exacta
          de ConvocatoriaInternaServicio.listarConvocatoriasCalificadas(interno)
          / listarAniosConvocatoriasCalificadas(interno) y de
          ProyectoServicio.listarAniosInicioProyectosCalificados(interno) /
          listarAniosFinProyectosCalificados(interno). Antes este endpoint
          devolvía SIEMPRE la variante sin filtrar para todo el mundo, lo que
          permitía elegir en el filtro convocatorias/años que no existen
          entre los proyectos externos (o internos) aprobados que se están
          listando.
        """
        interno_param = request.query_params.get("interno")

        if interno_param is not None:
            interno = interno_param.lower() in ("true", "1")
 
            convocatorias = list(
                ConvocatoriaSelector.listar_calificadas(interno)
                .values_list('nombre_convocatoria', flat=True)
            )
            anios_convocatoria = list(
                ConvocatoriaSelector.listar_anios_calificadas(interno)
            )
            anios_inicio = [
                d.year for d in ProyectoSelector.listar_anios_inicio_proyectos_calificados(interno)
            ]
            anios_fin = [
                d.year for d in ProyectoSelector.listar_anios_fin_proyectos_calificados(interno)
            ]
        else:
            convocatorias = list(
                Convocatoria.objects.order_by('nombre_convocatoria')
                .values_list('nombre_convocatoria', flat=True).distinct()
            )
            anios_inicio = [d.year for d in ProyectoSelector.listar_anios_inicio_distintos()]
            anios_fin = [d.year for d in ProyectoSelector.listar_anios_fin_distintos()]
            anios_convocatoria = [
                c.anio_convocatoria for c in Convocatoria.objects.exclude(anio_convocatoria__isnull=True)
                .order_by('-anio_convocatoria').distinct('anio_convocatoria')
            ]

        return Response({
            "convocatorias": convocatorias,
            "anios_inicio": anios_inicio,
            "anios_fin": anios_fin,
            "anios_convocatoria": anios_convocatoria,
        })
    
    @staticmethod
    def _parse_bool(valor):
        """
        Convierte un valor de query param (siempre string en HTTP) a bool
        real, o None si el parámetro no fue enviado (para omitir el filtro).
        NUNCA usar bool(str) directamente: bool("false") es True en Python,
        porque cualquier string no vacío es "truthy".
        """
        if valor is None or valor == '':
            return None
        if isinstance(valor, bool):
            return valor
        return str(valor).strip().lower() in ("true", "1")