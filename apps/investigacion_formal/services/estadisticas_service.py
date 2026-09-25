# apps/investigacion_formal/services/estadisticas_service.py
from apps.investigacion_formal.selectors.estadisticas_selector import EstadisticasSelector
from apps.investigacion_formal.selectors.convocatoria_selector import ConvocatoriaSelector
from apps.investigacion_formal.selectors.producto_minciencias_selector import ProductoMincienciasSelector
from apps.investigacion_formal.selectors.grupo_minciencias_selector import GrupoMincienciasSelector
from apps.institucional.selectors.facultad_escuela_selector import FacultadEscuelaSelector
from apps.institucional.selectors.grupo_investigacion_selector import GrupoInvestigacionSelector
from apps.investigacion_formal.services.avance_service import AvanceService


class EstadisticasService:

    # ------------------------------------------------------------------
    # Indicadores "por año" (ya existentes — sin cambios)
    # ------------------------------------------------------------------

    @staticmethod
    def proyectos_por_anio(interno=None, facultad_id=None, grupo_id=None):
        return list(EstadisticasSelector.proyectos_por_anio(
            interno=interno, facultad_id=facultad_id, grupo_id=grupo_id
        ))

    @staticmethod
    def finalizados_vs_en_ejecucion_por_anio(interno=None, facultad_id=None, grupo_id=None):
        return list(EstadisticasSelector.finalizados_vs_en_ejecucion_por_anio(
            interno=interno, facultad_id=facultad_id, grupo_id=grupo_id
        ))

    @staticmethod
    def ejecucion_presupuestal_promedio_por_anio(interno=None, facultad_id=None, grupo_id=None):
        return list(EstadisticasSelector.ejecucion_presupuestal_promedio_por_anio(
            interno=interno, facultad_id=facultad_id, grupo_id=grupo_id
        ))

    @staticmethod
    def produccion_por_anio(interno=None, facultad_id=None, grupo_id=None):
        return list(EstadisticasSelector.produccion_por_anio(
            interno=interno, facultad_id=facultad_id, grupo_id=grupo_id
        ))

    @staticmethod
    def avance_ponderado_promedio_por_anio(interno=None, facultad_id=None, grupo_id=None):
        pares = EstadisticasSelector.proyectos_por_anio_para_avance(
            interno=interno, facultad_id=facultad_id, grupo_id=grupo_id
        )
        acumulado_por_anio = {}
        conteo_por_anio = {}
        for par in pares:
            anio = par['anio']
            avance = AvanceService.calcular_avance_ponderado(par['id'])
            acumulado_por_anio[anio] = acumulado_por_anio.get(anio, 0) + avance
            conteo_por_anio[anio] = conteo_por_anio.get(anio, 0) + 1
        return [
            {
                "anio": anio,
                "promedio_avance": round(acumulado_por_anio[anio] / conteo_por_anio[anio], 2),
            }
            for anio in sorted(acumulado_por_anio)
        ]

    # ------------------------------------------------------------------
    # Indicadores "por entidad" — réplica de las 2 pantallas Thymeleaf
    # ------------------------------------------------------------------

    @staticmethod
    def proyectos_por_entidad(
        convocatoria=None, responsable=None, anio_inicio=None, anio_fin=None,
        interno=None, gruplac=None, estado=None,
    ):
        return EstadisticasSelector.proyectos_por_entidad(
            convocatoria=convocatoria, responsable=responsable, anio_inicio=anio_inicio,
            anio_fin=anio_fin, interno=interno, gruplac=gruplac, estado=estado,
        )

    @staticmethod
    def productos_por_entidad_anio(
        producto=None, responsable=None, grupo_minciencias=None, gruplac=None, estado=None,
    ):
        return EstadisticasSelector.productos_por_entidad_anio(
            producto=producto, responsable=responsable, grupo_minciencias=grupo_minciencias,
            gruplac=gruplac, estado=estado,
        )

    # ------------------------------------------------------------------
    # Catálogos para los filtros del tablero unificado. Orquesta selectores
    # de solo lectura de investigacion_formal e institucional en una sola
    # respuesta, para que el frontend no tenga que hacer 5 llamadas
    # (algunas paginadas) solo para llenar combos de filtro.
    # ------------------------------------------------------------------

    @staticmethod
    def opciones_filtro():
        return {
            "convocatorias": list(
                ConvocatoriaSelector.listar().values_list('nombre_convocatoria', flat=True)
            ),
            "facultades": list(
                FacultadEscuelaSelector.listar().values('id', 'nombre_facultad', 'abreviatura')
            ),
            "grupos": list(
                GrupoInvestigacionSelector.listar().values('id', 'nombre_grupo', 'sigla_grupo')
            ),
            "productos_minciencias": list(
                ProductoMincienciasSelector.listar().values_list('nombre_producto', flat=True)
            ),
            "grupos_minciencias": list(
                GrupoMincienciasSelector.listar().values_list('nombre_grupo_minciencias', flat=True)
            ),
        }