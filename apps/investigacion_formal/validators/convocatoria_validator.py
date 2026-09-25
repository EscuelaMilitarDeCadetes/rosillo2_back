from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.convocatoria_selector import ConvocatoriaSelector


class ConvocatoriaValidator:

    @staticmethod
    def validar_creacion(nombre_convocatoria, anio_convocatoria, inicio, cierre, interno):
        # NOTA: la restricción "solo ASESOR crea internas" se resuelve en
        # ConvocatoriaViewSet.create() forzando interno=True, no aquí.
        # Este validador es de dominio y debe aceptar interno=False cuando lo
        # invoca ProyectoService.crear_proyecto_externo() para la convocatoria
        # sintética de proyectos externos.
        ConvocatoriaValidator._validar_nombre(nombre_convocatoria)
        ConvocatoriaValidator._validar_anio(anio_convocatoria)
        ConvocatoriaValidator._validar_fechas(inicio, cierre)
        ConvocatoriaValidator._validar_interno(interno)
        ConvocatoriaValidator._validar_unicidad_nombre(nombre_convocatoria)

    @staticmethod
    def validar_cambio_estado(convocatoria, nuevo_estado):
        """La única modificación permitida sobre una convocatoria ya creada."""
        if nuevo_estado is None:
            raise ValidationError({"estado": "Debe indicar el nuevo estado de la convocatoria."})
        if convocatoria.estado == nuevo_estado:
            raise ValidationError(
                f"La convocatoria ya se encuentra en estado "
                f"{'activo' if nuevo_estado else 'inactivo'}."
            )

    @staticmethod
    def _validar_nombre(nombre_convocatoria):
        if not nombre_convocatoria or not nombre_convocatoria.strip():
            raise ValidationError({"nombre_convocatoria": "El nombre de la convocatoria es obligatorio."})
        if len(nombre_convocatoria) > 200:
            raise ValidationError(
                {"nombre_convocatoria": "El nombre supera el máximo de 200 caracteres."}
            )

    @staticmethod
    def _validar_anio(anio_convocatoria):
        if not anio_convocatoria:
            raise ValidationError({"anio_convocatoria": "El año de la convocatoria es obligatorio."})

    @staticmethod
    def _validar_fechas(inicio, cierre):
        if not inicio or not cierre:
            raise ValidationError(
                "Las fechas de inicio y cierre de la convocatoria son obligatorias."
            )
        if cierre < inicio:
            raise ValidationError(
                {"cierre": "La fecha de cierre no puede ser anterior a la fecha de inicio."}
            )

    @staticmethod
    def _validar_interno(interno):
        if interno is None:
            raise ValidationError(
                {"interno": "Debe indicar si la convocatoria es interna o externa."}
            )

    @staticmethod
    def _validar_unicidad_nombre(nombre_convocatoria, excluir_id=None):
        if ConvocatoriaSelector.existe_nombre(nombre_convocatoria, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_convocatoria": f"Ya existe una convocatoria con el nombre '{nombre_convocatoria}'."}
            )