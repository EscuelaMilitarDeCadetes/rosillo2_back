# apps/investigacion_formativa/services/estadisticas_service.py
from collections import defaultdict

from apps.investigacion_formativa.selectors.estadisticas_selector import EstadisticasSelector
from apps.investigacion_formativa.selectors.modalidad_selector import ModalidadSelector
from apps.investigacion_formativa.services.avance_service import AvanceService
from apps.institucional.selectors.facultad_escuela_selector import FacultadEscuelaSelector


class EstadisticasService:

    # ------------------------------------------------------------------
    # Indicadores "por año"
    # ------------------------------------------------------------------

    @staticmethod
    def procesos_por_anio(modalidad_id=None, facultad_id=None):
        return list(EstadisticasSelector.procesos_por_anio(
            modalidad_id=modalidad_id, facultad_id=facultad_id
        ))

    @staticmethod
    def aprobados_vs_reprobados_por_anio(modalidad_id=None, facultad_id=None):
        return list(EstadisticasSelector.aprobados_vs_no_aprobados_por_anio(
            modalidad_id=modalidad_id, facultad_id=facultad_id
        ))

    @staticmethod
    def procesos_por_estado_general(modalidad_id=None, facultad_id=None):
        return list(EstadisticasSelector.procesos_por_estado_general(
            modalidad_id=modalidad_id, facultad_id=facultad_id
        ))

    @staticmethod
    def segunda_instancia_por_anio(modalidad_id=None, facultad_id=None):
        return list(EstadisticasSelector.segunda_instancia_por_anio(
            modalidad_id=modalidad_id, facultad_id=facultad_id
        ))

    @staticmethod
    def certificaciones_por_tipo_y_anio(modalidad_id=None):
        return list(EstadisticasSelector.certificaciones_por_tipo_y_anio(
            modalidad_id=modalidad_id
        ))

    @staticmethod
    def distribucion_estado_actual(modalidad_id=None, facultad_id=None):
        """Cantidad de procesos agrupados por su estado_actual"""
        return EstadisticasSelector.distribucion_estado_actual(
            modalidad_id=modalidad_id, facultad_id=facultad_id
        )

    @staticmethod
    def promedio_avance_tiempo_por_anio(modalidad_id=None, facultad_id=None):
        filas = EstadisticasSelector.procesos_activos_por_anio_para_avance(
            modalidad_id=modalidad_id, facultad_id=facultad_id
        )
        avances_por_anio = defaultdict(list)
        for fila in filas:
            avance = AvanceService.calcular_avance_tiempo(fila['id'])
            avances_por_anio[fila['anio']].append(avance)

        return [
            {
                "anio": anio,
                "promedio_avance_tiempo": round(sum(valores) / len(valores), 2),
                "total_procesos": len(valores),
            }
            for anio, valores in sorted(avances_por_anio.items())
        ]

    # ------------------------------------------------------------------
    # Indicadores "por modalidad"
    # ------------------------------------------------------------------

    @staticmethod
    def procesos_por_modalidad(facultad_id=None):
        return list(EstadisticasSelector.procesos_por_modalidad(facultad_id=facultad_id))

    @staticmethod
    def promedio_nota_final_por_modalidad(facultad_id=None):
        return list(EstadisticasSelector.promedio_nota_final_por_modalidad(facultad_id=facultad_id))

    @staticmethod
    def promedio_porcentaje_avance_por_modalidad(facultad_id=None):
        return list(EstadisticasSelector.promedio_porcentaje_avance_por_modalidad(facultad_id=facultad_id))

    @staticmethod
    def tasa_aprobacion_por_modalidad(facultad_id=None):
        return EstadisticasSelector.tasa_aprobacion_por_modalidad(facultad_id=facultad_id)

    @staticmethod
    def promedio_horas_acumuladas_por_modalidad(facultad_id=None):
        return list(EstadisticasSelector.promedio_horas_acumuladas_por_modalidad(facultad_id=facultad_id))

    # ------------------------------------------------------------------
    # Catálogos para los filtros del tablero. orquesta selectores de solo
    # lectura de investigacion_formativa e institucional en una sola
    # respuesta, mismo patrón que investigacion_formal.EstadisticasService.
    # ------------------------------------------------------------------

    @staticmethod
    def opciones_filtro():
        return {
            "modalidades": list(
                ModalidadSelector.listar_activas().values('id', 'nombre', 'codigo')
            ),
            "facultades": list(
                FacultadEscuelaSelector.listar().values('id', 'nombre_facultad', 'abreviatura')
            ),
        }