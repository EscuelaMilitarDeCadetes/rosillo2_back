"""
Validador de Gerente.

Interfaz estándar definitiva más las reglas especiales confirmadas
explícitamente:
1. Solo un Gerente activo a la vez (validado aquí; el CIERRE del anterior
   ocurre en el Service, que es quien orquesta side-effects).
2. fecha_salida no puede ser anterior a fecha_ingreso.
3. 'persona' es obligatoria al crear.
"""
from rest_framework.exceptions import ValidationError
from apps.institucional.selectors.persona_selector import PersonaSelector
from apps.institucional.selectors.gerente_selector import GerenteSelector


class GerenteValidator:

    @staticmethod
    def validar_creacion(persona_id, fecha_ingreso, fecha_salida=None):
        """
        Usado por GerenteService.crear(). No valida 'no hay otro activo'
        porque crear() SIEMPRE cierra al anterior antes de llegar aquí —
        esa es la semántica de negocio de "asignar un nuevo Gerente".
        """
        GerenteValidator._validar_persona_obligatoria(persona_id)
        GerenteValidator._validar_persona_existe(persona_id)
        GerenteValidator._validar_fechas(fecha_ingreso, fecha_salida)

    @staticmethod
    def validar_actualizacion(gerente, nueva_fecha_ingreso, nueva_fecha_salida):
        GerenteValidator._validar_fechas(nueva_fecha_ingreso, nueva_fecha_salida)
        seria_activo = nueva_fecha_salida is None
        ya_era_el_activo = gerente.estado and gerente.fecha_salida is None
        if seria_activo and not ya_era_el_activo:
            GerenteValidator._validar_no_hay_otro_activo(gerente)
            
    @staticmethod
    def validar_eliminacion(gerente):
        pass

    @staticmethod
    def _validar_persona_obligatoria(persona_id):
        if not persona_id:
            raise ValidationError(
                {"persona": "Debe especificar la persona que ocupará el cargo de Gerente."}
            )

    @staticmethod
    def _validar_persona_existe(persona_id):
        if not PersonaSelector.existe(persona_id):
            raise ValidationError(
                {"persona": f"No existe una Persona con id={persona_id}."}
            )

    @staticmethod
    def _validar_fechas(fecha_ingreso, fecha_salida):
        if fecha_salida is not None and fecha_ingreso is not None:
            if fecha_salida < fecha_ingreso:
                raise ValidationError(
                    {"fecha_salida": (
                        f"La fecha de salida ({fecha_salida}) no puede ser "
                        f"anterior a la fecha de ingreso ({fecha_ingreso})."
                    )}
                )

    @staticmethod
    def _validar_no_hay_otro_activo(gerente):
        if GerenteSelector.existe_activo_distinto_de(excluir_id=gerente.pk):
            raise ValidationError(
                "Ya existe un Gerente activo en este momento. Use "
                "GerenteService.crear() para reemplazarlo de forma "
                "controlada, en lugar de reactivar este registro "
                "directamente."
            )