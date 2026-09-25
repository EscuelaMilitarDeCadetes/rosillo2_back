# apps/investigacion_formal/services/avance_service.py
from apps.investigacion_formal.selectors.avance_selector import AvanceSelector


class AvanceService:
    """
    Réplica corregida de ProyectosControlador.calcularAvancePonderado /
    calcularPromedioPorObjetivo del Thymeleaf original.

    NOTA DE AUDITORÍA: en el Thymeleaf original, calcularPromedioPorObjetivo()
    se invocaba SIEMPRE con la lista completa de puntos del proyecto (no la
    del objetivo puntual), por lo que el "peso" se cancelaba matemáticamente
    en la fórmula y el resultado final terminaba siendo, en la práctica, solo
    el promedio simple de avance de TODOS los puntos del proyecto — es decir,
    la ponderación por peso nunca se aplicaba de verdad pese a que el método
    se llamaba "avance ponderado". Esta versión corrige eso: el peso de cada
    objetivo sí pondera su aporte al resultado final del proyecto.
    """

    @staticmethod
    def calcular_promedio_por_objetivo(objetivo_id):
        """
        % de avance promedio de un objetivo específico
        = promedio del campo `avance` de sus ObjetivoXPunto activos.
        """
        puntos = list(AvanceSelector.listar_puntos_activos_por_objetivo(objetivo_id))
        if not puntos:
            return 0.0
        return sum(p.avance for p in puntos) / len(puntos)

    @staticmethod
    def calcular_peso_por_objetivo(objetivo_id):
        """
        Peso de un objetivo específico (columna "PESO X OBJETIVO" del Excel).
        CORREGIDO: el peso se define UNA VEZ por objetivo y se espera que
        todos sus PuntoControl compartan el mismo valor (p.ej. G5=30% para
        los 2 puntos del Objetivo 1, G8=40% para los 4 puntos del Objetivo 3).
        Se usa PROMEDIO en vez de SUMA para tolerar inconsistencias de
        captura sin duplicar el peso por cada punto adicional.
        """
        puntos = list(AvanceSelector.listar_puntos_activos_por_objetivo(objetivo_id))
        if not puntos:
            return 0.0
        return sum(p.punto_control.peso for p in puntos) / len(puntos)

    @staticmethod
    def calcular_detalle_por_objetivo(proyecto_id):
        """
        Devuelve, por cada objetivo específico del proyecto, su promedio y su
        peso — insumo directo para la ficha/tablero de seguimiento mensual.
        """
        objetivos = AvanceSelector.listar_objetivos_con_puntos_activos(proyecto_id)
        detalle = []
        for objetivo in objetivos:
            promedio = AvanceService.calcular_promedio_por_objetivo(objetivo.pk)
            peso = AvanceService.calcular_peso_por_objetivo(objetivo.pk)
            detalle.append({
                "objetivo_id": objetivo.pk,
                "objetivo": objetivo.objetivo,
                "clase": objetivo.clase,
                "promedio_avance": round(promedio, 2),
                "peso": peso,
            })
        return detalle

    @staticmethod
    def calcular_avance_ponderado(proyecto_id):
        """
        % de avance ponderado del proyecto
        = sum(promedio_objetivo_i * peso_objetivo_i) / sum(peso_objetivo_i)

        Si el proyecto no tiene objetivos con puntos de control activos,
        devuelve 0.0 (igual que el comportamiento original ante lista vacía).
        """
        detalle = AvanceService.calcular_detalle_por_objetivo(proyecto_id)
        total_peso = sum(item["peso"] for item in detalle)
        if total_peso <= 0:
            return 0.0
        suma_ponderada = sum(item["promedio_avance"] * item["peso"] for item in detalle)
        return round(suma_ponderada / total_peso, 2)
    
    @staticmethod
    def calcular_avance_tiempo(proyecto_id):
        """
        % de avance en tiempo del proyecto = tiempo transcurrido desde
        fecha_inicio / duración total (fecha_inicio -> fecha_fin).
        Equivalente a H3 = E3/19 del Excel y a
        ProyectosControlador.calculatePercentage() del Thymeleaf original
        (nunca migrado hasta ahora).
        """
        from django.utils import timezone
        from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector

        proyecto = ProyectoSelector.obtener(proyecto_id)
        if not proyecto.fecha_inicio or not proyecto.fecha_fin:
            return 0.0

        hoy = timezone.now().date()
        duracion_total = (proyecto.fecha_fin - proyecto.fecha_inicio).days
        if duracion_total <= 0:
            return 0.0

        transcurrido = (hoy - proyecto.fecha_inicio).days
        transcurrido = max(0, min(transcurrido, duracion_total))  # no negativo, no > 100%
        return round((transcurrido / duracion_total) * 100, 2)