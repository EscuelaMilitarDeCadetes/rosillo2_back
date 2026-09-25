# apps/investigacion_formal/selectors/estadisticas_selector.py
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import ExtractYear
from apps.investigacion_formal.selectors.responsable_proyecto import q_por_facultad, q_por_grupo

from apps.investigacion_formal.models import Proyecto, Monto


def _filtrar_proyecto_por_facultad_grupo(qs, facultad_id=None, grupo_id=None):
    if facultad_id is not None:
        qs = qs.filter(q_por_facultad(facultad_id, prefix=""))
    if grupo_id is not None:
        qs = qs.filter(q_por_grupo(grupo_id, prefix=""))
    return qs.distinct()

def _filtrar_monto_por_facultad_grupo(qs, facultad_id=None, grupo_id=None):
    if facultad_id is not None:
        qs = qs.filter(q_por_facultad(facultad_id, prefix="proyecto__"))
    if grupo_id is not None:
        qs = qs.filter(q_por_grupo(grupo_id, prefix="proyecto__"))
    return qs.distinct()


class EstadisticasSelector:

    # ------------------------------------------------------------------
    # Indicadores "por año" (ya existentes — sin cambios)
    # ------------------------------------------------------------------

    @staticmethod
    def proyectos_por_anio(interno=None, facultad_id=None, grupo_id=None):
        qs = Proyecto.objects.filter(fecha_inicio__isnull=False)
        if interno is not None:
            qs = qs.filter(interno=interno)
        qs = _filtrar_proyecto_por_facultad_grupo(qs, facultad_id, grupo_id)
        return (
            qs.annotate(anio=ExtractYear('fecha_inicio'))
            .values('anio')
            .annotate(total=Count('id'))
            .order_by('anio')
        )

    @staticmethod
    def finalizados_vs_en_ejecucion_por_anio(interno=None, facultad_id=None, grupo_id=None):
        qs = Proyecto.objects.filter(fecha_inicio__isnull=False)
        if interno is not None:
            qs = qs.filter(interno=interno)
        qs = _filtrar_proyecto_por_facultad_grupo(qs, facultad_id, grupo_id)
        return (
            qs.annotate(anio=ExtractYear('fecha_inicio'))
            .values('anio')
            .annotate(
                finalizados=Count('id', filter=Q(registro_acta_cierre=True)),
                en_ejecucion=Count('id', filter=Q(registro_acta_cierre=False)),
            )
            .order_by('anio')
        )

    @staticmethod
    def ejecucion_presupuestal_promedio_por_anio(interno=None, facultad_id=None, grupo_id=None):
        qs = Monto.objects.filter(proyecto__fecha_inicio__isnull=False)
        if interno is not None:
            qs = qs.filter(proyecto__interno=interno)
        qs = _filtrar_monto_por_facultad_grupo(qs, facultad_id, grupo_id)
        return (
            qs.annotate(anio=ExtractYear('proyecto__fecha_inicio'))
            .values('anio')
            .annotate(promedio_ejecutado=Avg('ejecutado'))
            .order_by('anio')
        )

    @staticmethod
    def proyectos_por_anio_para_avance(interno=None, facultad_id=None, grupo_id=None):
        qs = Proyecto.objects.filter(fecha_inicio__isnull=False)
        if interno is not None:
            qs = qs.filter(interno=interno)
        qs = _filtrar_proyecto_por_facultad_grupo(qs, facultad_id, grupo_id)
        return list(
            qs.annotate(anio=ExtractYear('fecha_inicio')).values('anio', 'id')
        )

    @staticmethod
    def produccion_por_anio(interno=None, facultad_id=None, grupo_id=None):
        qs = Proyecto.objects.filter(fecha_inicio__isnull=False, registro_acta_cierre=True)
        if interno is not None:
            qs = qs.filter(interno=interno)
        qs = _filtrar_proyecto_por_facultad_grupo(qs, facultad_id, grupo_id)
        return (
            qs.annotate(anio=ExtractYear('fecha_inicio'))
            .values('anio')
            .annotate(total=Count('id'))
            .order_by('anio')
        )

    # ------------------------------------------------------------------
    # Indicadores "por entidad" — réplica de las 2 pantallas Thymeleaf
    # originales (estadisticaProyectosEnDesarrollo.html /
    # estadisticaProyectosXConvocatoria.html). Ver EstadisticasService
    # para las notas de diseño sobre las divergencias encontradas frente
    # al GraficasEstadisticasController / EstadisticaContarProyectosEjecucionRepository
    # original.
    # ------------------------------------------------------------------

    @staticmethod
    def proyectos_por_entidad(
        convocatoria=None, responsable=None, anio_inicio=None, anio_fin=None,
        interno=None, gruplac=None, estado=None,
    ):
        """
        Réplica de EstadisticaContarProyectosEjecucionRepository.buscarEstadisticasProyectos
        (y, sin filtros, de getTodasFacultadesyGrupos). Cuenta proyectos con calificación
        finalizada y APROBADA en al menos una convocatoria, que siguen en ejecución
        (registro_acta_cierre=False), agrupados por facultad y por grupo de investigación
        del responsable — como dos conteos independientes (igual que el UNION original),
        no una sola distribución.
        """
        filtros = Q(
            proyectoxconvocatoria__estado_finalizado_calificacion=True,
            proyectoxconvocatoria__calificacion_ultimo_filtro_calificacion='APROBADO',
            registro_acta_cierre=False,
        )
        if convocatoria:
            filtros &= Q(proyectoxconvocatoria__convocatoria__nombre_convocatoria__icontains=convocatoria)
        if anio_inicio is not None:
            filtros &= Q(fecha_inicio__year=anio_inicio)
        if anio_fin is not None:
            filtros &= Q(fecha_fin__year=anio_fin)
        if interno is not None:
            filtros &= Q(proyectoxconvocatoria__convocatoria__interno=interno)
        if gruplac is not None:
            filtros &= Q(gruplac=gruplac)
        if estado is not None:
            filtros &= Q(estado=estado)

        base = Proyecto.objects.filter(filtros).distinct()

        qs_facultades = base.filter(
            usuario__asignaciones__estado=True,
            usuario__asignaciones__persona__personaxgrupo__estado=True,
            usuario__asignaciones__persona__personaxgrupo__facultad__isnull=False,
        )
        if responsable:
            qs_facultades = qs_facultades.filter(
                usuario__asignaciones__persona__personaxgrupo__facultad__abreviatura__icontains=responsable
            )
        facultades = (
            qs_facultades
            .annotate(nombre_entidad=F('usuario__asignaciones__persona__personaxgrupo__facultad__nombre_facultad'))
            .values('nombre_entidad')
            .annotate(total=Count('id', distinct=True))
            .order_by('nombre_entidad')
        )

        qs_grupos = base.filter(
            usuario__asignaciones__estado=True,
            usuario__asignaciones__persona__personaxgrupo__estado=True,
            usuario__asignaciones__persona__personaxgrupo__grupo__isnull=False,
        )
        if responsable:
            qs_grupos = qs_grupos.filter(
                usuario__asignaciones__persona__personaxgrupo__grupo__sigla_grupo__icontains=responsable
            )
        grupos = (
            qs_grupos
            .annotate(nombre_entidad=F('usuario__asignaciones__persona__personaxgrupo__grupo__sigla_grupo'))
            .values('nombre_entidad')
            .annotate(total=Count('id', distinct=True))
            .order_by('nombre_entidad')
        )

        return list(facultades) + list(grupos)

    @staticmethod
    def productos_por_entidad_anio(
        producto=None, responsable=None, grupo_minciencias=None, gruplac=None, estado=None,
    ):
        """
        Réplica de EstadisticaContarProyectosEjecucionRepository.buscarEstadisticasProductos.

        NOTA DE DISEÑO (divergencia consciente frente al Thymeleaf original): la query nativa
        de filtro múltiple (buscarEstadisticasProductos) omite "proyecto.registro_acta_cierre
        = false" y "producto_x_proyecto.entregado = true", condiciones que SÍ aplica la carga
        inicial sin filtros (getTodosProductosXAnio). Se interpreta como una inconsistencia del
        original y se decide mantener ambas condiciones siempre activas: de lo contrario, al
        aplicar cualquier filtro, un producto no entregado o de un proyecto ya cerrado
        aparecería en el conteo de "producción científica", contradiciendo tanto el título de
        la gráfica como el comportamiento de la vista inicial.

        Se agrupa únicamente por producto + año (igual que el original); el filtro de
        "responsable" acepta tanto abreviatura de facultad como sigla de grupo (equivalente al
        UNION de las dos ramas de la query nativa, pero como una sola condición OR).
        """
        filtros = Q(
            proyectoxconvocatoria__estado_finalizado_calificacion=True,
            proyectoxconvocatoria__calificacion_ultimo_filtro_calificacion='APROBADO',
            registro_acta_cierre=False,
            productoxproyecto__entregado=True,
        )
        if producto:
            filtros &= Q(productoxproyecto__producto_x_grupo__producto_minciencias__nombre_producto__icontains=producto)
        if grupo_minciencias:
            filtros &= Q(productoxproyecto__producto_x_grupo__grupo_minciencias__nombre_grupo_minciencias__icontains=grupo_minciencias)
        if gruplac is not None:
            filtros &= Q(productoxproyecto__gruplac=gruplac)
        if estado is not None:
            filtros &= Q(estado=estado)
        if responsable:
            filtros &= (
                Q(
                    usuario__asignaciones__estado=True,
                    usuario__asignaciones__persona__personaxgrupo__estado=True,
                    usuario__asignaciones__persona__personaxgrupo__facultad__abreviatura__icontains=responsable,
                ) | Q(
                    usuario__asignaciones__estado=True,
                    usuario__asignaciones__persona__personaxgrupo__estado=True,
                    usuario__asignaciones__persona__personaxgrupo__grupo__sigla_grupo__icontains=responsable,
                )
            )

        return list(
            Proyecto.objects.filter(filtros)
            .annotate(
                anio=ExtractYear('fecha_inicio'),
                nombre_entidad=F('productoxproyecto__producto_x_grupo__producto_minciencias__nombre_producto'),
            )
            .values('nombre_entidad', 'anio')
            .annotate(total=Count('productoxproyecto__id', distinct=True))
            .order_by('anio', 'nombre_entidad')
        )