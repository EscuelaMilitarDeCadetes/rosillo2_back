"""
Punto único para resolver y filtrar por el 'responsable' (facultad o
grupo de investigación) de un Proyecto, cubriendo los dos orígenes
posibles:
  - Interno: se deriva de PersonaXGrupo del usuario creador (FACULTAD/GRUPO).
  - Externo: se lee directamente de Proyecto.grupo_investigacion / .facultad,
    asignados explícitamente por CEXTERNO al crear el proyecto.
"""
from django.db.models import Q
from apps.institucional.models import PersonaXGrupo


def etiqueta_responsable(proyecto):
    """Devuelve la sigla/abreviatura a mostrar en reportes, o None."""
    if not proyecto.interno:
        if proyecto.facultad_id:
            return proyecto.facultad.abreviatura
        if proyecto.grupo_investigacion_id:
            return proyecto.grupo_investigacion.sigla_grupo
        return None

    pxg = (
        PersonaXGrupo.objects
        .filter(
            persona__asignaciones__usuario_id=proyecto.usuario_id,
            persona__asignaciones__estado=True,
            estado=True,
        )
        .select_related('facultad', 'grupo')
        .first()
    )
    if pxg is None:
        return None
    if pxg.facultad_id:
        return pxg.facultad.abreviatura
    if pxg.grupo_id:
        return pxg.grupo.sigla_grupo
    return None


def q_por_facultad(facultad_id, prefix=""):
    """Q-object para filtrar un queryset de Proyecto (o de un modelo que
    tenga FK 'proyecto', pasando prefix='proyecto__') por facultad
    responsable, cubriendo internos y externos."""
    p = prefix
    interno = Q(**{
        f"{p}interno": True,
        f"{p}usuario__asignaciones__estado": True,
        f"{p}usuario__asignaciones__persona__personaxgrupo__estado": True,
        f"{p}usuario__asignaciones__persona__personaxgrupo__facultad_id": facultad_id,
    })
    externo = Q(**{f"{p}interno": False, f"{p}facultad_id": facultad_id})
    return interno | externo


def q_por_grupo(grupo_id, prefix=""):
    p = prefix
    interno = Q(**{
        f"{p}interno": True,
        f"{p}usuario__asignaciones__estado": True,
        f"{p}usuario__asignaciones__persona__personaxgrupo__estado": True,
        f"{p}usuario__asignaciones__persona__personaxgrupo__grupo_id": grupo_id,
    })
    externo = Q(**{f"{p}interno": False, f"{p}grupo_investigacion_id": grupo_id})
    return interno | externo


def q_por_responsable_codificado(responsable, prefix=""):
    """Réplica del encoding 'FAC:'+abreviatura / 'GRU:'+sigla usado en
    buscar_con_filtros(responsable=...)."""
    p = prefix
    if responsable.startswith('FAC:'):
        abreviatura = responsable[len('FAC:'):]
        interno = Q(**{
            f"{p}interno": True,
            f"{p}usuario__asignaciones__estado": True,
            f"{p}usuario__asignaciones__persona__personaxgrupo__estado": True,
            f"{p}usuario__asignaciones__persona__personaxgrupo__facultad__abreviatura": abreviatura,
        })
        externo = Q(**{f"{p}interno": False, f"{p}facultad__abreviatura": abreviatura})
        return interno | externo
    if responsable.startswith('GRU:'):
        sigla = responsable[len('GRU:'):]
        interno = Q(**{
            f"{p}interno": True,
            f"{p}usuario__asignaciones__estado": True,
            f"{p}usuario__asignaciones__persona__personaxgrupo__estado": True,
            f"{p}usuario__asignaciones__persona__personaxgrupo__grupo__sigla_grupo": sigla,
        })
        externo = Q(**{f"{p}interno": False, f"{p}grupo_investigacion__sigla_grupo": sigla})
        return interno | externo
    return Q()