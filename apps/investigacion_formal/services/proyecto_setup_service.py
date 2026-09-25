# apps/investigacion_formal/services/proyecto_setup_service.py
from apps.common.services.tarea_service import TareaService
from apps.investigacion_formal.selectors.investigador_x_proyecto_selector import InvestigadorXProyectoSelector
from apps.investigacion_formal.selectors.objetivos_selector import ObjetivosSelector
from apps.investigacion_formal.selectors.producto_x_proyecto_selector import ProductoXProyectoSelector
from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector


class ProyectoSetupService:

    @staticmethod
    def verificar_configuracion_completa(proyecto_id, ejecutor):
        """Si el proyecto ya tiene al menos un investigador, un producto y un
        objetivo, recuerda a su responsable registrar avance y el informe."""
        proyecto = ProyectoSelector.obtener(proyecto_id)
        tiene_investigadores = InvestigadorXProyectoSelector.listar_por_proyecto(proyecto_id).exists()
        tiene_productos = ProductoXProyectoSelector.listar_por_proyecto(proyecto_id).exists()
        tiene_objetivos = ObjetivosSelector.listar_por_proyecto(proyecto_id).exists()
        if tiene_investigadores and tiene_productos and tiene_objetivos:
            TareaService.crear_recordatorio(
                usuario_id=proyecto.usuario_id,
                descripcion=(
                    f"Registrar avance y generar el informe de seguimiento "
                    f"del proyecto '{proyecto.titulo}'"
                ),
                objeto=proyecto,
                ejecutor=ejecutor,
            )