from rest_framework.exceptions import ValidationError
from apps.crm.selectors.entidad_externa_selector import EntidadExternaSelector

MEDIOS_VALIDOS = {'REUNION', 'CONVENIO'}


class InteraccionValidator:

    @staticmethod
    def validar_creacion(entidad_id, medio, resumen, proyecto_asociado_id=None):
        InteraccionValidator._validar_entidad(entidad_id)
        InteraccionValidator._validar_medio(medio)
        InteraccionValidator._validar_resumen(resumen)
        InteraccionValidator._validar_proyecto_asociado(proyecto_asociado_id)

    @staticmethod
    def validar_actualizacion(interaccion_id, entidad_id, medio, resumen, proyecto_asociado_id=None):
        InteraccionValidator._validar_entidad(entidad_id)
        InteraccionValidator._validar_medio(medio)
        InteraccionValidator._validar_resumen(resumen)
        InteraccionValidator._validar_proyecto_asociado(proyecto_asociado_id)

    @staticmethod
    def validar_eliminacion(interaccion):
        pass

    @staticmethod
    def _validar_entidad(entidad_id):
        if not entidad_id:
            raise ValidationError({"entidad": "La entidad externa es obligatoria."})
        if not EntidadExternaSelector.existe(entidad_id):
            raise ValidationError({"entidad": f"No existe una EntidadExterna con id={entidad_id}."})

    @staticmethod
    def _validar_medio(medio):
        if not medio:
            raise ValidationError({"medio": "El medio de la interacción es obligatorio."})
        if medio not in MEDIOS_VALIDOS:
            raise ValidationError(
                {"medio": f"'{medio}' no es un medio válido. Use uno de: {sorted(MEDIOS_VALIDOS)}."}
            )

    @staticmethod
    def _validar_resumen(resumen):
        if not resumen or not resumen.strip():
            raise ValidationError({"resumen": "El resumen de la interacción es obligatorio."})

    @staticmethod
    def _validar_proyecto_asociado(proyecto_asociado_id):
        if proyecto_asociado_id is None:
            return  # el modelo permite null=True
        from apps.investigacion_formal.models import Proyecto
        if not Proyecto.objects.filter(pk=proyecto_asociado_id).exists():
            raise ValidationError(
                {"proyecto_asociado": f"No existe un Proyecto con id={proyecto_asociado_id}."}
            )