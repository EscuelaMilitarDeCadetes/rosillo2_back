# apps/investigacion_formal/selectors/proyecto_x_convocatoria_selector.py
from apps.investigacion_formal.models import ProyectoXConvocatoria
from django.db.models import Exists, OuterRef
from apps.investigacion_formal.models import InvestigadorXProyecto, ProductoXProyecto
from apps.investigacion_formal.models.objetivos import Objetivos
from apps.investigacion_formal.selectors.responsable_proyecto import (
    q_por_facultad, q_por_grupo, q_por_responsable_codificado,
)

class ProyectoXConvocatoriaSelector:

    @staticmethod
    def listar():
        return ProyectoXConvocatoria.objects.select_related('convocatoria', 'proyecto').all()

    @staticmethod
    def obtener(proyecto_x_convocatoria_id):
        return (
            ProyectoXConvocatoria.objects
            .select_related('convocatoria', 'proyecto')
            .get(pk=proyecto_x_convocatoria_id)
        )

    @staticmethod
    def existe(proyecto_x_convocatoria_id):
        return ProyectoXConvocatoria.objects.filter(pk=proyecto_x_convocatoria_id).exists()

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return (
            ProyectoXConvocatoria.objects
            .select_related('convocatoria')
            .filter(proyecto_id=proyecto_id)
        )

    @staticmethod
    def listar_por_convocatoria(convocatoria_id):
        return (
            ProyectoXConvocatoria.objects
            .select_related('proyecto')
            .filter(convocatoria_id=convocatoria_id)
        )

    @staticmethod
    def listar_por_usuario(usuario_id):
        return (
            ProyectoXConvocatoria.objects
            .select_related("proyecto", "convocatoria")
            .filter(proyecto__usuario_id=usuario_id)
        )

    @staticmethod
    def existe_vinculo(proyecto_id, convocatoria_id, excluir_id=None):
        qs = ProyectoXConvocatoria.objects.filter(
            proyecto_id=proyecto_id, convocatoria_id=convocatoria_id
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_sin_calificar():
        return (
            ProyectoXConvocatoria.objects
            .select_related('convocatoria', 'proyecto')
            .filter(estado_finalizado_calificacion=False, convocatoria__estado=False)
        )

    @staticmethod
    def listar_calificados(calificacion=None):
        """calificacion opcional: 'APROBADO' | 'NO_APROBADO'."""
        qs = (
            ProyectoXConvocatoria.objects
            .select_related('convocatoria', 'proyecto')
            .filter(estado_finalizado_calificacion=True)
        )
        if calificacion is not None:
            qs = qs.filter(calificacion_ultimo_filtro_calificacion=calificacion)
        return qs

    @staticmethod
    def listar_por_facultad(facultad_id):
        return (
            ProyectoXConvocatoria.objects
            .select_related('convocatoria', 'proyecto')
            .filter(q_por_facultad(facultad_id, prefix="proyecto__"))
            .distinct()
        )

    @staticmethod
    def listar_por_grupo(grupo_id):
        return (
            ProyectoXConvocatoria.objects
            .select_related('convocatoria', 'proyecto')
            .filter(q_por_grupo(grupo_id, prefix="proyecto__"))
            .distinct()
        )

    @staticmethod
    def buscar_con_filtros(convocatoria=None, codigo=None, titulo=None,
                            financiado=None, alianza=None, responsable=None,
                            calificacion=None, anio_inicio=None, anio_fin=None,
                            interno=None, gruplac=None, estado=None,
                            facultad_id=None, grupo_id=None,
                            estado_finalizado_calificacion=None,
                            anio_convocatoria=None):
        """
        'responsable' filtra por persona (nombre/apellido) — el
        responsable real de un proyecto es la Facultad o el Grupo, no la
        persona (ver ProyectoXConvocatoriaSerializer.get_responsable, que ya
        devuelve facultad.abreviatura / grupo.sigla_grupo, no un nombre).
        Ahora replica el mismo encoding del dropdown original de Thymeleaf:
        'FAC:'+abreviatura / 'GRU:'+sigla_grupo.
        'anio_convocatoria' filtra Convocatoria.anio_convocatoria
        (año de la convocatoria), distinto de anio_inicio/anio_fin que
        filtran las fechas del PROYECTO.
        se agregan facultad_id/grupo_id/estado_finalizado_calificacion
        para dar soporte server-side (con paginación real) a
        calificarProyectosXFacultad.html / calificarProyectosXGrupo.html, que
        antes solo tenían por-facultad/{id}/ y por-grupo/{id}/ (sin filtros
        combinables ni paginación). El resto de la firma no cambia.
        """
        from django.db.models import Q
        qs = ProyectoXConvocatoria.objects.select_related(
            'proyecto', 'convocatoria'
        ).all()
        filtros = Q()
        if convocatoria:
            filtros &= Q(convocatoria__nombre_convocatoria__icontains=convocatoria)
        if codigo:
            filtros &= Q(proyecto__codigo__icontains=codigo)
        if titulo:
            filtros &= Q(proyecto__titulo__icontains=titulo)
        if financiado is not None:
            filtros &= Q(proyecto__financiado=financiado)
        if alianza is not None:
            filtros &= Q(proyecto__alianza=alianza)
        if responsable:
            filtros &= q_por_responsable_codificado(responsable, prefix="proyecto__")
        if facultad_id is not None:
            filtros &= q_por_facultad(facultad_id, prefix="proyecto__")
        if grupo_id is not None:
            filtros &= q_por_grupo(grupo_id, prefix="proyecto__")
        if calificacion:
            filtros &= Q(calificacion_ultimo_filtro_calificacion=calificacion)
        if estado_finalizado_calificacion is not None:
            filtros &= Q(estado_finalizado_calificacion=estado_finalizado_calificacion)
        if anio_inicio:
            filtros &= Q(proyecto__fecha_inicio__year=anio_inicio)
        if anio_fin:
            filtros &= Q(proyecto__fecha_fin__year=anio_fin)
        if anio_convocatoria:
            filtros &= Q(convocatoria__anio_convocatoria=anio_convocatoria)
        if interno is not None:
            filtros &= Q(convocatoria__interno=interno)
        if gruplac is not None:
            filtros &= Q(proyecto__gruplac=gruplac)
        if estado is not None:
            filtros &= Q(estado=estado)
        qs = qs.annotate(
            tiene_investigadores=Exists(
                InvestigadorXProyecto.objects.filter(proyecto_id=OuterRef('proyecto_id'), estado=True)
            ),
            tiene_productos=Exists(
                ProductoXProyecto.objects.filter(proyecto_id=OuterRef('proyecto_id'))
            ),
            tiene_objetivos=Exists(
                Objetivos.objects.filter(proyecto_id=OuterRef('proyecto_id'), estado=True)
            ),
        )
        return qs.filter(filtros).distinct().order_by('-proyecto__fecha_inicio')