# apps/investigacion_formativa/validators/modalidad_validator.py

from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.modalidad_selector import ModalidadSelector


class ModalidadValidator:

    @staticmethod
    def validar_creacion(nombre, codigo, descripcion, requiere_evaluadores, requiere_tutor,
                          requiere_antiplagio, requiere_sustentacion, cantidad_maxima_estudiantes,
                          cantidad_minima_evaluadores, permite_homologacion, requiere_producto_final):
        ModalidadValidator._validar_nombre(nombre)
        ModalidadValidator._validar_codigo(codigo)
        ModalidadValidator._validar_cantidad_maxima_estudiantes(cantidad_maxima_estudiantes)
        ModalidadValidator._validar_cantidad_minima_evaluadores(cantidad_minima_evaluadores)
        ModalidadValidator._validar_booleano_o_none(requiere_evaluadores, "requiere_evaluadores", permitir_none=False)
        ModalidadValidator._validar_booleano_o_none(requiere_tutor, "requiere_tutor")
        ModalidadValidator._validar_booleano_o_none(requiere_antiplagio, "requiere_antiplagio")
        ModalidadValidator._validar_booleano_o_none(requiere_sustentacion, "requiere_sustentacion")
        ModalidadValidator._validar_booleano_o_none(permite_homologacion, "permite_homologacion")
        ModalidadValidator._validar_booleano_o_none(requiere_producto_final, "requiere_producto_final")
        ModalidadValidator.validar_consistencia_evaluadores(requiere_evaluadores, cantidad_minima_evaluadores)
        ModalidadValidator._validar_unicidad_nombre(nombre)

    @staticmethod
    def validar_actualizacion(modalidad, nombre, codigo, descripcion, requiere_evaluadores, requiere_tutor,
                               requiere_antiplagio, requiere_sustentacion, cantidad_maxima_estudiantes,
                               cantidad_minima_evaluadores, permite_homologacion, requiere_producto_final):
        ModalidadValidator._validar_nombre(nombre)
        ModalidadValidator._validar_codigo(codigo)
        ModalidadValidator._validar_cantidad_maxima_estudiantes(cantidad_maxima_estudiantes)
        ModalidadValidator._validar_cantidad_minima_evaluadores(cantidad_minima_evaluadores)
        ModalidadValidator._validar_booleano_o_none(requiere_evaluadores, "requiere_evaluadores", permitir_none=False)
        ModalidadValidator._validar_booleano_o_none(requiere_tutor, "requiere_tutor")
        ModalidadValidator._validar_booleano_o_none(requiere_antiplagio, "requiere_antiplagio")
        ModalidadValidator._validar_booleano_o_none(requiere_sustentacion, "requiere_sustentacion")
        ModalidadValidator._validar_booleano_o_none(permite_homologacion, "permite_homologacion")
        ModalidadValidator._validar_booleano_o_none(requiere_producto_final, "requiere_producto_final")
        ModalidadValidator.validar_consistencia_evaluadores(requiere_evaluadores, cantidad_minima_evaluadores)
        ModalidadValidator._validar_unicidad_nombre(nombre, excluir_id=modalidad.pk)

    @staticmethod
    def validar_activacion(modalidad):
        if modalidad.activo:
            raise ValidationError("Esta modalidad ya se encuentra activa.")

    @staticmethod
    def validar_eliminacion(modalidad):
        if not modalidad.activo:
            raise ValidationError("Esta modalidad ya se encuentra desactivada.")

    @staticmethod
    def validar_consistencia_evaluadores(requiere_evaluadores, cantidad_minima_evaluadores):
        """Si la modalidad exige evaluadores, debe indicarse cuántos como mínimo."""
        if requiere_evaluadores and not cantidad_minima_evaluadores:
            raise ValidationError(
                {"cantidad_minima_evaluadores": "Debe indicar la cantidad mínima de evaluadores para esta modalidad."}
            )

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre de la modalidad es obligatorio."})
        if len(nombre) > 150:
            raise ValidationError({"nombre": "El nombre supera el máximo de 150 caracteres."})

    @staticmethod
    def _validar_codigo(codigo):
        if not codigo or not codigo.strip():
            raise ValidationError({"codigo": "El código de la modalidad es obligatorio."})
        if len(codigo) > 100:
            raise ValidationError({"codigo": "El código supera el máximo de 100 caracteres."})

    @staticmethod
    def _validar_cantidad_maxima_estudiantes(cantidad_maxima_estudiantes):
        if cantidad_maxima_estudiantes is None:
            return
        try:
            valor = float(cantidad_maxima_estudiantes)
        except (TypeError, ValueError):
            raise ValidationError(
                {"cantidad_maxima_estudiantes": "La cantidad máxima de estudiantes debe ser numérica."}
            )
        if valor < 1:
            raise ValidationError(
                {"cantidad_maxima_estudiantes": "La cantidad máxima de estudiantes debe ser al menos 1."}
            )

    @staticmethod
    def _validar_cantidad_minima_evaluadores(cantidad_minima_evaluadores):
        if cantidad_minima_evaluadores is None:
            return
        try:
            valor = int(cantidad_minima_evaluadores)
        except (TypeError, ValueError):
            raise ValidationError(
                {"cantidad_minima_evaluadores": "La cantidad mínima de evaluadores debe ser un entero."}
            )
        if valor < 1:
            raise ValidationError(
                {"cantidad_minima_evaluadores": "La cantidad mínima de evaluadores debe ser al menos 1."}
            )

    @staticmethod
    def _validar_booleano_o_none(valor, campo, permitir_none=True):
        if valor is None:
            if permitir_none:
                return
            raise ValidationError({campo: f"El campo '{campo}' es obligatorio."})
        if not isinstance(valor, bool):
            raise ValidationError({campo: f"El campo '{campo}' debe ser verdadero o falso."})

    @staticmethod
    def _validar_unicidad_nombre(nombre, excluir_id=None):
        if ModalidadSelector.existe_nombre(nombre, excluir_id=excluir_id):
            raise ValidationError({"nombre": f"Ya existe una modalidad con el nombre '{nombre}'."})