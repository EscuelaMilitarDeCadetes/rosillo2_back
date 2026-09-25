"""
Validador de FacultadEscuela.

Interfaz estándar definitiva.
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.facultad_escuela_selector import FacultadEscuelaSelector


class FacultadEscuelaValidator:

    @staticmethod
    def validar_creacion(nombre_facultad, abreviatura):
        FacultadEscuelaValidator._validar_nombre(nombre_facultad)
        FacultadEscuelaValidator._validar_abreviatura(abreviatura)
        FacultadEscuelaValidator._validar_unicidad_nombre(nombre_facultad)
        FacultadEscuelaValidator._validar_unicidad_abreviatura(abreviatura)

    @staticmethod
    def validar_actualizacion(facultad_id, nombre_facultad, abreviatura):
        FacultadEscuelaValidator._validar_nombre(nombre_facultad)
        FacultadEscuelaValidator._validar_abreviatura(abreviatura)
        FacultadEscuelaValidator._validar_unicidad_nombre(nombre_facultad, excluir_id=facultad_id)
        FacultadEscuelaValidator._validar_unicidad_abreviatura(abreviatura, excluir_id=facultad_id)

    @staticmethod
    def _validar_nombre(nombre_facultad):
        if not nombre_facultad or not nombre_facultad.strip():
            raise ValidationError({"nombre_facultad": "El nombre de la facultad es obligatorio."})
        if len(nombre_facultad) > 30:
            raise ValidationError(
                {"nombre_facultad": f"El nombre '{nombre_facultad}' supera el máximo de 30 caracteres."}
            )

    @staticmethod
    def _validar_abreviatura(abreviatura):
        if not abreviatura or not abreviatura.strip():
            raise ValidationError({"abreviatura": "La abreviatura es obligatoria."})
        if len(abreviatura) > 5:
            raise ValidationError(
                {"abreviatura": f"La abreviatura '{abreviatura}' supera el máximo de 5 caracteres."}
            )

    @staticmethod
    def _validar_unicidad_nombre(nombre_facultad, excluir_id=None):
        if FacultadEscuelaSelector.existe_nombre(nombre_facultad, excluir_id=excluir_id):
            raise ValidationError(
                {"nombre_facultad": f"Ya existe una facultad con el nombre '{nombre_facultad}'."}
            )

    @staticmethod
    def _validar_unicidad_abreviatura(abreviatura, excluir_id=None):
        if FacultadEscuelaSelector.existe_abreviatura(abreviatura, excluir_id=excluir_id):
            raise ValidationError(
                {"abreviatura": f"Ya existe una facultad con la abreviatura '{abreviatura}'."}
            )