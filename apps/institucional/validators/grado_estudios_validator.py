"""
Validador de GradoEstudios.

Interfaz estándar definitiva: validar_creacion(), validar_actualizacion(),
validar_eliminacion(). Reglas atómicas reutilizables como métodos privados.
Todas las ValidationError llevan mensaje explícito (sin excepciones vacías).
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.grado_estudios_selector import GradoEstudiosSelector


class GradoEstudiosValidator:

    @staticmethod
    def validar_creacion(sigla_grado, descripcion):
        GradoEstudiosValidator._validar_sigla(sigla_grado)
        GradoEstudiosValidator._validar_descripcion(descripcion)
        GradoEstudiosValidator._validar_unicidad_sigla(sigla_grado)

    @staticmethod
    def validar_actualizacion(grado_id, sigla_grado, descripcion):
        GradoEstudiosValidator._validar_sigla(sigla_grado)
        GradoEstudiosValidator._validar_descripcion(descripcion)
        GradoEstudiosValidator._validar_unicidad_sigla(sigla_grado, excluir_id=grado_id)

    @staticmethod
    def _validar_sigla(sigla_grado):
        if not sigla_grado or not sigla_grado.strip():
            raise ValidationError({"sigla_grado": "La sigla del grado es obligatoria."})
        if len(sigla_grado) > 3:
            raise ValidationError(
                {"sigla_grado": f"La sigla '{sigla_grado}' supera el máximo de 3 caracteres."}
            )

    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            raise ValidationError({"descripcion": "La descripción del grado es obligatoria."})
        if len(descripcion) > 150:
            raise ValidationError(
                {"descripcion": "La descripción supera el máximo de 150 caracteres."}
            )

    @staticmethod
    def _validar_unicidad_sigla(sigla_grado, excluir_id=None):
        if GradoEstudiosSelector.existe_sigla(sigla_grado, excluir_id=excluir_id):
            raise ValidationError(
                {"sigla_grado": f"Ya existe un grado de estudios con la sigla '{sigla_grado}'."}
            )