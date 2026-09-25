# apps/investigacion_formativa/views/estadisticas_viewset.py
from apps.usuarios.permissions.tiene_ambito import TieneAmbitoFormativa
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investigacion_formativa.services.estadisticas_service import EstadisticasService
from apps.investigacion_formativa.permissions import combinar, ROLES_LECTURA_INVESTIGACION_FORMATIVA


class EstadisticasViewSet(viewsets.ViewSet):

    def get_permissions(self):
        return [combinar(ROLES_LECTURA_INVESTIGACION_FORMATIVA), TieneAmbitoFormativa()]

    # ------------------------------------------------------------------
    # Indicadores "por año"
    # ------------------------------------------------------------------

    @action(detail=False, methods=["get"], url_path="procesos-por-anio")
    def procesos_por_anio(self, request):
        filtros = self._parse_filtros_modalidad_facultad(request)
        return Response(EstadisticasService.procesos_por_anio(**filtros))

    @action(detail=False, methods=["get"], url_path="aprobados-vs-reprobados-por-anio")
    def aprobados_vs_reprobados_por_anio(self, request):
        filtros = self._parse_filtros_modalidad_facultad(request)
        return Response(EstadisticasService.aprobados_vs_reprobados_por_anio(**filtros))

    @action(detail=False, methods=["get"], url_path="procesos-por-estado-general")
    def procesos_por_estado_general(self, request):
        filtros = self._parse_filtros_modalidad_facultad(request)
        return Response(EstadisticasService.procesos_por_estado_general(**filtros))

    @action(detail=False, methods=["get"], url_path="segunda-instancia-por-anio")
    def segunda_instancia_por_anio(self, request):
        filtros = self._parse_filtros_modalidad_facultad(request)
        return Response(EstadisticasService.segunda_instancia_por_anio(**filtros))

    @action(detail=False, methods=["get"], url_path="distribucion-estado-actual")
    def distribucion_estado_actual(self, request):
        filtros = self._parse_filtros_modalidad_facultad(request)
        return Response(EstadisticasService.distribucion_estado_actual(**filtros))

    @action(detail=False, methods=["get"], url_path="certificaciones-por-tipo-y-anio")
    def certificaciones_por_tipo_y_anio(self, request):
        modalidad_id = request.query_params.get("modalidad_id")
        return Response(EstadisticasService.certificaciones_por_tipo_y_anio(
            modalidad_id=int(modalidad_id) if modalidad_id else None,
        ))

    # ------------------------------------------------------------------
    # Indicadores "por modalidad"
    # ------------------------------------------------------------------

    @action(detail=False, methods=["get"], url_path="procesos-por-modalidad")
    def procesos_por_modalidad(self, request):
        facultad_id = request.query_params.get("facultad_id")
        return Response(EstadisticasService.procesos_por_modalidad(
            facultad_id=int(facultad_id) if facultad_id else None,
        ))

    @action(detail=False, methods=["get"], url_path="promedio-nota-final-por-modalidad")
    def promedio_nota_final_por_modalidad(self, request):
        facultad_id = request.query_params.get("facultad_id")
        return Response(EstadisticasService.promedio_nota_final_por_modalidad(
            facultad_id=int(facultad_id) if facultad_id else None,
        ))

    @action(detail=False, methods=["get"], url_path="promedio-avance-por-modalidad")
    def promedio_avance_por_modalidad(self, request):
        facultad_id = request.query_params.get("facultad_id")
        return Response(EstadisticasService.promedio_porcentaje_avance_por_modalidad(
            facultad_id=int(facultad_id) if facultad_id else None,
        ))

    @action(detail=False, methods=["get"], url_path="tasa-aprobacion-por-modalidad")
    def tasa_aprobacion_por_modalidad(self, request):
        facultad_id = request.query_params.get("facultad_id")
        return Response(EstadisticasService.tasa_aprobacion_por_modalidad(
            facultad_id=int(facultad_id) if facultad_id else None,
        ))

    @action(detail=False, methods=["get"], url_path="promedio-horas-acumuladas-por-modalidad")
    def promedio_horas_acumuladas_por_modalidad(self, request):
        facultad_id = request.query_params.get("facultad_id")
        return Response(EstadisticasService.promedio_horas_acumuladas_por_modalidad(
            facultad_id=int(facultad_id) if facultad_id else None,
        ))

    @action(detail=False, methods=["get"], url_path="promedio-avance-tiempo-por-anio")
    def promedio_avance_tiempo_por_anio(self, request):
        filtros = self._parse_filtros_modalidad_facultad(request)
        return Response(EstadisticasService.promedio_avance_tiempo_por_anio(**filtros))

    # ------------------------------------------------------------------
    # Catálogos para los filtros del tablero
    # ------------------------------------------------------------------

    @action(detail=False, methods=["get"], url_path="filtros")
    def filtros(self, request):
        return Response(EstadisticasService.opciones_filtro())

    # ------------------------------------------------------------------

    @staticmethod
    def _parse_filtros_modalidad_facultad(request):
        modalidad_id = request.query_params.get("modalidad_id")
        facultad_id = request.query_params.get("facultad_id")
        return {
            "modalidad_id": int(modalidad_id) if modalidad_id else None,
            "facultad_id": int(facultad_id) if facultad_id else None,
        }