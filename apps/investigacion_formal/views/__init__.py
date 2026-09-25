from .calificacion_viewset import CalificacionViewSet
from .control_cambios_viewset import ControlCambiosViewSet
from .convocatoria_viewset import ConvocatoriaViewSet
from .ejecucion_viewset import EjecucionViewSet
from .estadisticas_viewset import EstadisticasViewSet
from .grupo_minciencias_viewset import GrupoMincienciasViewSet
from .investigador_x_proyecto_viewset import InvestigadorXProyectoViewSet
from .monto_viewset import MontoViewSet
from .objetivo_x_punto_viewset import ObjetivoXPuntoViewSet
from .objetivos_viewset import ObjetivosViewSet
from .producto_minciencias_viewset import ProductoMincienciasViewSet
from .producto_x_grupo_viewset import ProductoXGrupoViewSet
from .producto_x_proyecto_viewset import ProductoXProyectoViewSet
from .proyecto_x_convocatoria_viewset import ProyectoXConvocatoriaViewSet
from .proyecto_viewset import ProyectoViewSet
from .punto_control_viewset import PuntoControlViewSet
from .rol_investigador_viewset import RolInvestigadorViewSet
from .tipo_calificacion_viewset import TipoCalificacionViewSet
from .tipo_producto_viewset import TipoProductoViewSet
from .tipo_rubro_viewset import TipoRubroViewSet

__all__ = [
    "CalificacionViewSet",
    "ControlCambiosViewSet",
    "ConvocatoriaViewSet",
    "EjecucionViewSet",
    "EstadisticasViewSet",
    "GrupoMincienciasViewSet",
    "InvestigadorXProyectoViewSet",
    "MontoViewSet",
    "ObjetivoXPuntoViewSet",
    "ObjetivosViewSet",
    "ProductoMincienciasViewSet",
    "ProductoXGrupoViewSet",
    "ProductoXProyectoViewSet",
    "ProyectoXConvocatoriaViewSet",
    "ProyectoViewSet",
    "PuntoControlViewSet",
    "RolInvestigadorViewSet",
    "TipoCalificacionViewSet",
    "TipoProductoViewSet",
    "TipoRubroViewSet"
]