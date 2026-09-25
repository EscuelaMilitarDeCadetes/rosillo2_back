"""
Validador de Persona.

Interfaz: validar_creacion(), validar_actualizacion(). NO existe
validar_eliminacion() — Persona es un registro permanente, el "retiro"
se modela vía PersonaXGrupo.desvinculacion/estado, nunca eliminando la
Persona en sí.

Reglas reflejan las constraints reales del modelo:
    documento = CharField(max_length=20, unique=True)
    celular   = CharField(max_length=20, unique=True)
    correo    = EmailField(max_length=150, unique=True)
    nombre, apellido = CharField(max_length=80)
    cvlac     = CharField(max_length=150, blank=True, null=True)
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.persona_selector import PersonaSelector
from apps.institucional.selectors.grado_estudios_selector import GradoEstudiosSelector


class PersonaValidator:

    @staticmethod
    def validar_creacion(grado_id, nombre, apellido, documento, celular, correo, cvlac=None):
        PersonaValidator._validar_grado(grado_id)
        PersonaValidator._validar_nombre(nombre)
        PersonaValidator._validar_apellido(apellido)
        PersonaValidator._validar_documento(documento)
        PersonaValidator._validar_celular(celular)
        PersonaValidator._validar_correo(correo)
        PersonaValidator._validar_cvlac(cvlac)
        PersonaValidator._validar_unicidad_documento(documento)
        PersonaValidator._validar_unicidad_celular(celular)
        PersonaValidator._validar_unicidad_correo(correo)

    @staticmethod
    def validar_actualizacion(persona_id, grado_id, nombre, apellido, documento, celular, correo, cvlac=None):
        PersonaValidator._validar_grado(grado_id)
        PersonaValidator._validar_nombre(nombre)
        PersonaValidator._validar_apellido(apellido)
        PersonaValidator._validar_documento(documento)
        PersonaValidator._validar_celular(celular)
        PersonaValidator._validar_correo(correo)
        PersonaValidator._validar_cvlac(cvlac)
        PersonaValidator._validar_unicidad_documento(documento, excluir_id=persona_id)
        PersonaValidator._validar_unicidad_celular(celular, excluir_id=persona_id)
        PersonaValidator._validar_unicidad_correo(correo, excluir_id=persona_id)

    @staticmethod
    def _validar_grado(grado_id):
        if not grado_id:
            raise ValidationError({"grado": "El grado de estudios es obligatorio."})
        if not GradoEstudiosSelector.buscar(grado_id):
            raise ValidationError({"grado": f"No existe un GradoEstudios con id={grado_id}."})

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre es obligatorio."})
        if len(nombre) > 80:
            raise ValidationError({"nombre": f"El nombre '{nombre}' supera el máximo de 80 caracteres."})

    @staticmethod
    def _validar_apellido(apellido):
        if not apellido or not apellido.strip():
            raise ValidationError({"apellido": "El apellido es obligatorio."})
        if len(apellido) > 80:
            raise ValidationError({"apellido": f"El apellido '{apellido}' supera el máximo de 80 caracteres."})

    @staticmethod
    def _validar_documento(documento):
        if not documento or not documento.strip():
            raise ValidationError({"documento": "El documento es obligatorio."})
        if len(documento) > 20:
            raise ValidationError({"documento": "El documento supera el máximo de 20 caracteres."})

    @staticmethod
    def _validar_celular(celular):
        if not celular or not celular.strip():
            raise ValidationError({"celular": "El celular es obligatorio."})
        if len(celular) > 20:
            raise ValidationError({"celular": "El celular supera el máximo de 20 caracteres."})

    @staticmethod
    def _validar_correo(correo):
        if not correo or not correo.strip():
            raise ValidationError({"correo": "El correo es obligatorio."})
        if len(correo) > 150:
            raise ValidationError({"correo": "El correo supera el máximo de 150 caracteres."})
        if "@" not in correo:
            raise ValidationError({"correo": f"'{correo}' no es un correo electrónico válido."})

    @staticmethod
    def _validar_cvlac(cvlac):
        if cvlac is not None and len(cvlac) > 150:
            raise ValidationError({"cvlac": "El CvLAC supera el máximo de 150 caracteres."})

    @staticmethod
    def _validar_unicidad_documento(documento, excluir_id=None):
        if PersonaSelector.existe_documento(documento, excluir_id=excluir_id):
            raise ValidationError(
                {"documento": f"Ya existe una persona registrada con el documento '{documento}'."}
            )

    @staticmethod
    def _validar_unicidad_celular(celular, excluir_id=None):
        if PersonaSelector.existe_celular(celular, excluir_id=excluir_id):
            raise ValidationError(
                {"celular": f"Ya existe una persona registrada con el celular '{celular}'."}
            )

    @staticmethod
    def _validar_unicidad_correo(correo, excluir_id=None):
        if PersonaSelector.existe_correo(correo, excluir_id=excluir_id):
            raise ValidationError(
                {"correo": f"Ya existe una persona registrada con el correo '{correo}'."}
            )