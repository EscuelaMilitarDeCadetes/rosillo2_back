from apps.investigacion_formal.views.estadisticas_viewset import EstadisticasViewSet
from rest_framework.routers import DefaultRouter

from apps.investigacion_formal.views.calificacion_viewset import CalificacionViewSet
from apps.investigacion_formal.views.control_cambios_viewset import ControlCambiosViewSet
from apps.investigacion_formal.views.convocatoria_viewset import ConvocatoriaViewSet
from apps.investigacion_formal.views.ejecucion_viewset import EjecucionViewSet
from apps.investigacion_formal.views.grupo_minciencias_viewset import GrupoMincienciasViewSet
from apps.investigacion_formal.views.investigador_x_proyecto_viewset import (
    InvestigadorXProyectoViewSet,
)
from apps.investigacion_formal.views.monto_viewset import MontoViewSet
from apps.investigacion_formal.views.objetivo_x_punto_viewset import ObjetivoXPuntoViewSet
from apps.investigacion_formal.views.objetivos_viewset import ObjetivosViewSet
from apps.investigacion_formal.views.producto_minciencias_viewset import (
    ProductoMincienciasViewSet,
)
from apps.investigacion_formal.views.producto_x_grupo_viewset import ProductoXGrupoViewSet
from apps.investigacion_formal.views.producto_x_proyecto_viewset import (
    ProductoXProyectoViewSet,
)
from apps.investigacion_formal.views.proyecto_viewset import ProyectoViewSet
from apps.investigacion_formal.views.proyecto_x_convocatoria_viewset import (
    ProyectoXConvocatoriaViewSet,
)
from apps.investigacion_formal.views.punto_control_viewset import PuntoControlViewSet
from apps.investigacion_formal.views.rol_investigador_viewset import RolInvestigadorViewSet
from apps.investigacion_formal.views.tipo_calificacion_viewset import TipoCalificacionViewSet
from apps.investigacion_formal.views.tipo_producto_viewset import TipoProductoViewSet
from apps.investigacion_formal.views.tipo_rubro_viewset import TipoRubroViewSet

router = DefaultRouter()

router.register(r'calificaciones', CalificacionViewSet, basename='calificacion')
router.register(r'control-cambios', ControlCambiosViewSet, basename='control-cambios')
router.register(r'convocatorias', ConvocatoriaViewSet, basename='convocatoria')
router.register(r'ejecuciones', EjecucionViewSet, basename='ejecucion')
router.register(r'estadisticas', EstadisticasViewSet, basename='estadisticas')
router.register(r'grupos-minciencias', GrupoMincienciasViewSet, basename='grupo-minciencias')
router.register(r'investigadores', InvestigadorXProyectoViewSet, basename='investigador-x-proyecto')
router.register(r'montos', MontoViewSet, basename='monto')
router.register(r'objetivo-punto', ObjetivoXPuntoViewSet, basename='objetivo-x-punto')
router.register(r'objetivos', ObjetivosViewSet, basename='objetivos')
router.register(r'productos-minciencias', ProductoMincienciasViewSet, basename='producto-minciencias')
router.register(r'productos-grupo', ProductoXGrupoViewSet, basename='producto-x-grupo')
router.register(r'productos-proyecto', ProductoXProyectoViewSet, basename='producto-x-proyecto')
router.register(r'proyectos', ProyectoViewSet, basename='proyecto')
router.register(r'proyecto-convocatoria', ProyectoXConvocatoriaViewSet, basename='proyecto-x-convocatoria')
router.register(r'puntos-control', PuntoControlViewSet, basename='punto-control')
router.register(r'roles-investigador', RolInvestigadorViewSet, basename='rol-investigador')
router.register(r'tipos-calificacion', TipoCalificacionViewSet, basename='tipo-calificacion')
router.register(r'tipos-producto', TipoProductoViewSet, basename='tipo-producto')
router.register(r'tipos-rubro', TipoRubroViewSet, basename='tipo-rubro')

urlpatterns = router.urls