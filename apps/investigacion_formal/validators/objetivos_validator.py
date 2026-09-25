from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector
from apps.investigacion_formal.selectors.objetivos_selector import ObjetivosSelector

CLASES_VALIDAS = {'PRINCIPAL', 'ESPECIFICO'}


class ObjetivosValidator:

    @staticmethod
    def validar_creacion(proyecto_id, objetivo, clase):
        ObjetivosValidator._validar_proyecto(proyecto_id)
        ObjetivosValidator._validar_objetivo(objetivo)
        ObjetivosValidator._validar_clase(clase)
        ObjetivosValidator._validar_unicidad_texto(objetivo)
        if clase == 'PRINCIPAL':
            ObjetivosValidator._validar_no_duplicar_objetivo_general(proyecto_id)

    @staticmethod
    def validar_actualizacion(objetivo_id, proyecto_id, objetivo, clase):
        ObjetivosValidator._validar_proyecto(proyecto_id)
        ObjetivosValidator._validar_objetivo(objetivo)
        ObjetivosValidator._validar_clase(clase)
        ObjetivosValidator._validar_unicidad_texto(objetivo, excluir_id=objetivo_id)

    @staticmethod
    def validar_eliminacion(objetivos):
        if not objetivos.estado:
            raise ValidationError("Este objetivo ya se encuentra desactivado.")

    @staticmethod
    def _validar_proyecto(proyecto_id):
        if not proyecto_id:
            raise ValidationError({"proyecto": "El proyecto es obligatorio."})
        if not ProyectoSelector.existe(proyecto_id):
            raise ValidationError({"proyecto": f"No existe un Proyecto con id={proyecto_id}."})

    @staticmethod
    def _validar_objetivo(objetivo):
        if not objetivo or not objetivo.strip():
            raise ValidationError({"objetivo": "El texto del objetivo es obligatorio."})
        if len(objetivo) > 255:
            raise ValidationError({"objetivo": "El objetivo supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_clase(clase):
        if clase not in CLASES_VALIDAS:
            raise ValidationError(
                {"clase": f"'{clase}' no es una clase válida. Use uno de: {sorted(CLASES_VALIDAS)}."}
            )

    @staticmethod
    def _validar_unicidad_texto(objetivo, excluir_id=None):
        if ObjetivosSelector.existe_texto(objetivo, excluir_id=excluir_id):
            raise ValidationError(
                {"objetivo": f"Ya existe un objetivo registrado con el texto '{objetivo}'."}
            )

    @staticmethod
    def _validar_no_duplicar_objetivo_general(proyecto_id):
        if ObjetivosSelector.existe_objetivo_general(proyecto_id):
            raise ValidationError(
                "Este proyecto ya tiene registrado un objetivo general (PRINCIPAL). "
                "Solo puede existir uno por proyecto."
            )