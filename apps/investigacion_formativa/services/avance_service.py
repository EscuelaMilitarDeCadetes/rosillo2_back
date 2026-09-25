from django.db import transaction
from django.utils import timezone

from apps.investigacion_formativa.selectors.instancia_etapa_selector import InstanciaEtapaSelector
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)
from apps.common.services.historial_service import HistorialService


class AvanceService:
    """
    Los métodos de cálculo son puros; solo porcentaje_avance() persiste, 
    porque porcentaje_avance es un campo almacenado, 
    a diferencia de Proyecto en investigacion_formal.
    """

    @staticmethod
    def calcular_avance_por_etapas(proceso_id):
        """% de avance = etapas APROBADO / total de etapas del flujo del proceso."""
        instancias = list(InstanciaEtapaSelector.listar_por_proceso(proceso_id))
        if not instancias:
            return 0.0
        aprobadas = sum(1 for i in instancias if i.estado == 'APROBADO')
        return round((aprobadas / len(instancias)) * 100, 2)

    @staticmethod
    def calcular_avance_tiempo(proceso_id):
        """% de avance en tiempo = tiempo transcurrido desde fecha_inicio / duración total."""
        proceso = ProcesoFormativoSelector.obtener(proceso_id)
        if not proceso.fecha_inicio or not proceso.fecha_fin:
            return 0.0
        hoy = timezone.now().date()
        duracion_total = (proceso.fecha_fin - proceso.fecha_inicio).days
        if duracion_total <= 0:
            return 0.0
        transcurrido = (hoy - proceso.fecha_inicio).days
        transcurrido = max(0, min(transcurrido, duracion_total))
        return round((transcurrido / duracion_total) * 100, 2)

    @staticmethod
    @transaction.atomic
    def actualizar_porcentaje_avance(proceso_id, ejecutor):
        """Recalcula el avance por etapas y lo persiste en
        ProcesoFormativo.porcentaje_avance (el avance en tiempo es informativo
        y no se guarda: se expone solo para tableros de seguimiento)."""
        proceso = ProcesoFormativoSelector.obtener(proceso_id)
        nuevo_porcentaje = AvanceService.calcular_avance_por_etapas(proceso_id)
        proceso.porcentaje_avance = nuevo_porcentaje
        proceso.save(update_fields=['porcentaje_avance'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el porcentaje de avance del proceso '{proceso.titulo}' a "
            f"{nuevo_porcentaje}% (id={proceso.pk}).",
            objeto=proceso,
        )
        return proceso
    
    @staticmethod
    def obtener_resumen(proceso_id):
        from apps.investigacion_formativa.selectors.avance_selector import AvanceSelector
        proceso = ProcesoFormativoSelector.obtener(proceso_id)
        control_horas = AvanceSelector.obtener_control_horas(proceso_id)
        ultimo_registro = AvanceSelector.obtener_ultimo_registro(proceso_id)
        instancia_actual = AvanceSelector.obtener_instancia_actual(proceso_id)
        etapa_actual = None
        if instancia_actual is not None:
            etapa_actual = {
                "instancia_id": instancia_actual.pk,
                "etapa_id": instancia_actual.etapa_id,
                "etapa_nombre": instancia_actual.etapa.nombre,
                "orden": instancia_actual.etapa.orden,
                "estado": instancia_actual.estado,
                "fecha_inicio": instancia_actual.fecha_inicio,
            }
        ultimo_registro_data = None
        if ultimo_registro is not None:
            ultimo_registro_data = {
                "registro_id": ultimo_registro.pk,
                "tipo_periodo": ultimo_registro.tipo_periodo,
                "fecha_periodo": ultimo_registro.fecha_periodo,
                "horas_reportadas": ultimo_registro.horas_reportadas,
                "aprobado": ultimo_registro.aprobado,
            }
        return {
            "proceso_id": proceso.pk,
            "porcentaje_avance": proceso.porcentaje_avance,
            "avance_tiempo": AvanceService.calcular_avance_tiempo(proceso_id),
            "horas_acumuladas": control_horas.horas_acumuladas if control_horas else None,
            "etapas_aprobadas": AvanceSelector.contar_etapas_aprobadas(proceso_id),
            "etapas_totales": AvanceSelector.contar_etapas_totales(proceso_id),
            "en_segunda_instancia": AvanceSelector.existe_etapa_en_segunda_instancia(proceso_id),
            "etapa_actual": etapa_actual,
            "ultimo_registro": ultimo_registro_data,
        }