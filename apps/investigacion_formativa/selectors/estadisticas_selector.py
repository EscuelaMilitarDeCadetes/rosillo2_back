# apps/investigacion_formativa/selectors/estadisticas_selector.py

from collections import Counter

from django.db.models import Count, Avg, Q
from django.db.models.functions import ExtractYear

from apps.investigacion_formativa.models import ProcesoFormativo, CertificacionExterna


def _filtrar_proceso_por_modalidad_facultad(qs, modalidad_id=None, facultad_id=None):
    if modalidad_id is not None:
        qs = qs.filter(flujo_version__modalidad_id=modalidad_id)
    if facultad_id is not None:
        qs = qs.filter(
            participantes__rol_en_modalidad='ESTUDIANTE',
            participantes__persona__estudiante__modalidad_facultad__facultad_id=facultad_id,
        )
    return qs.distinct()


class EstadisticasSelector:

    @staticmethod
    def procesos_por_anio(modalidad_id=None, facultad_id=None):
        qs = ProcesoFormativo.objects.filter(fecha_inicio__isnull=False)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, modalidad_id, facultad_id)
        return (
            qs.annotate(anio=ExtractYear('fecha_inicio'))
            .values('anio')
            .annotate(total=Count('id'))
            .order_by('anio')
        )

    @staticmethod
    def procesos_por_modalidad(facultad_id=None):
        qs = ProcesoFormativo.objects.filter(flujo_version__isnull=False)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, None, facultad_id)
        return (
            qs.values('flujo_version__modalidad__nombre')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

    @staticmethod
    def aprobados_vs_no_aprobados_por_anio(modalidad_id=None, facultad_id=None):
        qs = ProcesoFormativo.objects.filter(fecha_inicio__isnull=False, aprobado__isnull=False)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, modalidad_id, facultad_id)
        return (
            qs.annotate(anio=ExtractYear('fecha_inicio'))
            .values('anio')
            .annotate(
                aprobados=Count('id', filter=Q(aprobado=True)),
                no_aprobados=Count('id', filter=Q(aprobado=False)),
            )
            .order_by('anio')
        )

    @staticmethod
    def promedio_nota_final_por_modalidad(facultad_id=None):
        qs = ProcesoFormativo.objects.filter(nota_final__isnull=False)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, None, facultad_id)
        return (
            qs.values('flujo_version__modalidad__nombre')
            .annotate(promedio=Avg('nota_final'))
            .order_by('-promedio')
        )

    @staticmethod
    def procesos_por_estado_general(modalidad_id=None, facultad_id=None):
        qs = ProcesoFormativo.objects.all()
        qs = _filtrar_proceso_por_modalidad_facultad(qs, modalidad_id, facultad_id)
        return (
            qs.values('estado_general')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

    @staticmethod
    def segunda_instancia_por_anio(modalidad_id=None, facultad_id=None):
        qs = ProcesoFormativo.objects.filter(
            fecha_inicio__isnull=False, segunda_instancia_consumida=True
        )
        qs = _filtrar_proceso_por_modalidad_facultad(qs, modalidad_id, facultad_id)
        return (
            qs.annotate(anio=ExtractYear('fecha_inicio'))
            .values('anio')
            .annotate(total=Count('id'))
            .order_by('anio')
        )

    @staticmethod
    def promedio_porcentaje_avance_por_modalidad(facultad_id=None):
        qs = ProcesoFormativo.objects.filter(porcentaje_avance__isnull=False, activo=True)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, None, facultad_id)
        return (
            qs.values('flujo_version__modalidad__nombre')
            .annotate(promedio_avance=Avg('porcentaje_avance'))
            .order_by('-promedio_avance')
        )

    @staticmethod
    def certificaciones_por_tipo_y_anio(modalidad_id=None):
        qs = CertificacionExterna.objects.filter(fecha_inicio__isnull=False)
        if modalidad_id is not None:
            qs = qs.filter(proceso__flujo_version__modalidad_id=modalidad_id)
        return (
            qs.annotate(anio=ExtractYear('fecha_inicio'))
            .values('anio', 'tipo')
            .annotate(total=Count('id'))
            .order_by('anio', 'tipo')
        )

    @staticmethod
    def procesos_activos_por_anio_para_avance(modalidad_id=None, facultad_id=None):
        qs = ProcesoFormativo.objects.filter(fecha_inicio__isnull=False, activo=True)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, modalidad_id, facultad_id)
        return list(
            qs.annotate(anio=ExtractYear('fecha_inicio')).values('anio', 'id')
        )

    @staticmethod
    def tasa_aprobacion_por_modalidad(facultad_id=None):
        """% de procesos con aprobado=True sobre el total resuelto (aprobado no nulo),
        agrupado por modalidad."""
        qs = ProcesoFormativo.objects.filter(aprobado__isnull=False)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, None, facultad_id)
        filas = (
            qs.values('flujo_version__modalidad__nombre')
            .annotate(
                total=Count('id'),
                aprobados=Count('id', filter=Q(aprobado=True)),
            )
            .order_by('-total')
        )
        resultado = []
        for fila in filas:
            total = fila['total']
            tasa = (fila['aprobados'] / total * 100) if total else 0
            resultado.append({
                'modalidad': fila['flujo_version__modalidad__nombre'],
                'total': total,
                'aprobados': fila['aprobados'],
                'tasa_aprobacion': round(tasa, 2),
            })
        return resultado

    @staticmethod
    def promedio_horas_acumuladas_por_modalidad(facultad_id=None):
        qs = ProcesoFormativo.objects.filter(horas_acumuladas__isnull=False)
        qs = _filtrar_proceso_por_modalidad_facultad(qs, None, facultad_id)
        return (
            qs.values('flujo_version__modalidad__nombre')
            .annotate(promedio_horas=Avg('horas_acumuladas'))
            .order_by('-promedio_horas')
        )

    @staticmethod
    def distribucion_estado_actual(modalidad_id=None, facultad_id=None):
        """Cantidad de procesos agrupados por su estado_actual (propiedad calculada a
        partir de InstanciaEtapa: SIN_INICIAR/PENDIENTE/EN_PROCESO/RECHAZADO/
        SEGUNDA_INSTANCIA/FINALIZADO). No es un campo de BD, así que no se puede
        agregar con .values()/.annotate(); se cuenta en Python."""
        qs = ProcesoFormativo.objects.all()
        qs = _filtrar_proceso_por_modalidad_facultad(qs, modalidad_id, facultad_id)
        qs = qs.prefetch_related('instanciaetapa_set__etapa')
        conteo = Counter(proceso.estado_actual for proceso in qs)
        return [{'estado_actual': estado, 'total': total} for estado, total in conteo.items()]