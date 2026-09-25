from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.convocatoria_selector import ConvocatoriaSelector
from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector
from apps.investigacion_formal.selectors.proyecto_x_convocatoria_selector import (
    ProyectoXConvocatoriaSelector,
)


class ProyectoXConvocatoriaValidator:

    @staticmethod
    def validar_creacion(convocatoria_id, proyecto_id):
        ProyectoXConvocatoriaValidator._validar_convocatoria(convocatoria_id)
        ProyectoXConvocatoriaValidator._validar_proyecto(proyecto_id)
        ProyectoXConvocatoriaValidator._validar_convocatoria_activa(convocatoria_id)
        ProyectoXConvocatoriaValidator._validar_unicidad(convocatoria_id, proyecto_id)
        
    @staticmethod
    def validar_creacion_ya_finalizado(convocatoria_id, proyecto_id):
        """
        Variante de validar_creacion() exclusiva para proyectos externos
        (ProyectoXConvocatoriaService.crear_ya_finalizado_aprobado): la
        convocatoria sintética se crea y se cierra (estado=False) en el
        mismo acto por diseño (ConvocatoriaService.crear_proyecto_externo),
        así que a diferencia de la postulación normal NO debe exigirse que
        esté activa.
        """
        ProyectoXConvocatoriaValidator._validar_convocatoria(convocatoria_id)
        ProyectoXConvocatoriaValidator._validar_proyecto(proyecto_id)
        ProyectoXConvocatoriaValidator._validar_unicidad(convocatoria_id, proyecto_id)

    @staticmethod
    def validar_habilitar_correccion(proyecto_x_convocatoria):
        if proyecto_x_convocatoria.estado_finalizado_calificacion:
            raise ValidationError(
                "No se puede habilitar la corrección de documentos de un proyecto "
                "cuya calificación ya fue finalizada."
            )
        if proyecto_x_convocatoria.modificacion_documento_proyecto:
            raise ValidationError("La corrección de documentos ya se encuentra habilitada.")

    @staticmethod
    def validar_deshabilitar_correccion(proyecto_x_convocatoria):
        if not proyecto_x_convocatoria.modificacion_documento_proyecto:
            raise ValidationError("La corrección de documentos ya se encuentra deshabilitada.")

    @staticmethod
    def validar_finalizar_calificacion(proyecto_x_convocatoria, aprobado):
        if proyecto_x_convocatoria.estado_finalizado_calificacion:
            raise ValidationError(
                "La calificación de este proyecto-convocatoria ya fue finalizada."
            )
        if aprobado is None:
            raise ValidationError(
                {"aprobado": "Debe indicar si el proyecto fue aprobado o no en esta convocatoria."}
            )

    @staticmethod
    def validar_eliminacion(proyecto_x_convocatoria):
        if not proyecto_x_convocatoria.estado:
            raise ValidationError("Este proyecto-convocatoria ya se encuentra desactivado.")

    @staticmethod
    def _validar_convocatoria(convocatoria_id):
        if not convocatoria_id:
            raise ValidationError({"convocatoria": "La convocatoria es obligatoria."})
        if not ConvocatoriaSelector.existe(convocatoria_id):
            raise ValidationError(
                {"convocatoria": f"No existe una Convocatoria con id={convocatoria_id}."}
            )

    @staticmethod
    def _validar_proyecto(proyecto_id):
        if not proyecto_id:
            raise ValidationError({"proyecto": "El proyecto es obligatorio."})
        if not ProyectoSelector.existe(proyecto_id):
            raise ValidationError({"proyecto": f"No existe un Proyecto con id={proyecto_id}."})

    @staticmethod
    def _validar_convocatoria_activa(convocatoria_id):
        convocatoria = ConvocatoriaSelector.buscar(convocatoria_id)
        if convocatoria is not None and not convocatoria.estado:
            raise ValidationError(
                "No se puede postular un proyecto a una convocatoria que ya se "
                "encuentra cerrada/inactiva."
            )

    @staticmethod
    def _validar_unicidad(convocatoria_id, proyecto_id, excluir_id=None):
        if ProyectoXConvocatoriaSelector.existe_vinculo(
            proyecto_id, convocatoria_id, excluir_id=excluir_id
        ):
            raise ValidationError(
                "Este proyecto ya está registrado en esta misma convocatoria."
            )