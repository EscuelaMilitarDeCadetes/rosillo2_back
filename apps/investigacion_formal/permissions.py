"""
Combinaciones de permisos reutilizadas por múltiples ViewSets del módulo
investigacion_formal. Existe para evitar que la misma combinación de roles
se repita textualmente en 10 archivos distintos,: un cambio de política de 
roles se hace UNA vez aquí, no en cada ViewSet.

IMPORTANTE: estas son listas de CLASES de permiso (no instancias). Cada
ViewSet las combina con | dentro de su propio get_permissions(), igual que
antes — este archivo no cambia el comportamiento, solo centraliza la lista.
"""
from apps.investigacion_formal.selectors.objetivo_x_punto_selector import ObjetivoXPuntoSelector
from apps.investigacion_formal.selectors.objetivos_selector import ObjetivosSelector
from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector
from rest_framework.permissions import BasePermission
from apps.usuarios.permissions import (
    EsFacultad, EsGrupo, EsCInterno, EsCExterno,
    EsAsesor, EsSupervisor, EsDecano, EsGerente, EsSoporte,
)

# Roles operativos que pueden CONSULTAR (list/retrieve) la mayoría de
# recursos de investigacion_formal: todo el que participa del flujo de
# investigación formal en algún rol.
ROLES_LECTURA_INVESTIGACION_FORMAL = [
    EsFacultad, EsGrupo, EsCInterno, EsCExterno,
    EsAsesor, EsSupervisor, EsDecano, EsGerente,
]

# Mismo grupo anterior + Soporte, para los catálogos administrados por
# Soporte (GrupoMinciencias, ProductoMinciencias, ProductoXGrupo,
# RolInvestigador, TipoCalificacion, TipoProducto, TipoRubro).
ROLES_LECTURA_CATALOGOS = ROLES_LECTURA_INVESTIGACION_FORMAL + [EsSoporte]

# Roles que pueden ejecutar operaciones de escritura sobre proyectos/objetivos/
# ejecuciones ya en curso (no creación inicial, sino gestión posterior).
ROLES_ESCRITURA_GESTION = [EsCInterno, EsCExterno]

# Roles que pueden crear registros operativos nuevos (proyectos, objetivos,
# investigadores) — Facultad/Grupo son quienes ejecutan directamente el
# proyecto en campo.
ROLES_CREACION_OPERATIVA = [EsFacultad, EsGrupo, EsCInterno, EsCExterno]

# Roles que pueden CREAR un proyecto (no una convocatoria externa, no
# gestión posterior): solo quienes ejecutan directamente el proyecto en
# campo, igual que ROLES_CREACION_OPERATIVA pero restringido a estos dos
# — se separa como constante propia porque Proyecto/ProyectoXConvocatoria
# deliberadamente NO permiten crear a CInterno/CExterno (ver ACCIONES_SOLO_CINTERNO_CEXTERNO).
ROLES_CREACION_PROYECTO = [EsFacultad, EsGrupo]

# Roles de consulta específicos del flujo de Calificacion (no coincide con
# ROLES_LECTURA_INVESTIGACION_FORMAL: aquí NO participan Facultad/Grupo
# directamente, solo quienes intervienen en el proceso de calificación).
ROLES_CONSULTA_CALIFICACION = [EsSupervisor, EsCInterno, EsCExterno]

# Roles que ven la tabla de convocatorias abiertas en el inicio
ROLES_VEN_CONVOCATORIAS_ABIERTAS = [EsAsesor, EsCInterno, EsFacultad, EsGrupo]



def combinar(clases_permiso):
    """Azúcar sintáctico: instancia y combina con | una lista de clases."""
    permiso_combinado = clases_permiso[0]
    for clase in clases_permiso[1:]:
        permiso_combinado = permiso_combinado | clase
    return permiso_combinado()


class ProyectoTieneActaInicio(BasePermission):
    """
    Bloquea a FACULTAD/GRUPO en acciones que dependen de que el proyecto ya
    tenga cargada el acta de inicio. CINTERNO/CEXTERNO no se ven afectados.
    """
    message = "Esta acción se habilita cuando CINTERNO cargue el acta de inicio del proyecto."

    def has_permission(self, request, view):
        if request.user.has_role('CINTERNO') or request.user.has_role('CEXTERNO'):
            return True
        proyecto_id = self._resolver_proyecto_id(request, view)
        if not proyecto_id:
            return True  # que falle más adelante por validación normal, no aquí
        return ProyectoSelector.tiene_acta_inicio(proyecto_id)

    @staticmethod
    def _resolver_proyecto_id(request, view):
        # Investigador, Objetivos (general/específico), Producto: el body trae "proyecto".
        proyecto_id = request.data.get('proyecto') or view.kwargs.get('proyecto_id')
        if proyecto_id:
            return proyecto_id
        # ObjetivoXPuntoViewSet.create: el body trae "objetivo", no "proyecto".
        objetivo_id = request.data.get('objetivo')
        if objetivo_id:
            objetivo = ObjetivosSelector.obtener(objetivo_id)
            return objetivo.proyecto_id if objetivo else None
        # ObjetivoXPuntoViewSet.agregar_avance: la URL trae "punto_control_id".
        punto_control_id = view.kwargs.get('punto_control_id')
        if punto_control_id:
            vinculo = ObjetivoXPuntoSelector.obtener_activo_por_punto_control(punto_control_id)
            return vinculo.objetivo.proyecto_id if vinculo else None
        return None