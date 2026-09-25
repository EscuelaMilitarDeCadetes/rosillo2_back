from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)
from apps.investigacion_formativa.selectors.flujo_proceso_selector import FlujoProcesoSelector
from apps.investigacion_formativa.selectors.banco_ideas_selector import BancoIdeasSelector

PALABRAS_CLAVE_MAX_LEN = 200
TITULO_MAX_LEN = 500


class ProcesoFormativoValidator:

    @staticmethod
    def validar_creacion(flujo_version_id, titulo, observacion, fecha_inicio, fecha_fin,
                          idea_id=None, entidad_externa_id=None, palabras_clave=None,
                          requiere_sustentacion=False, permite_segunda_instancia=False):
        ProcesoFormativoValidator._validar_flujo_version(flujo_version_id)
        ProcesoFormativoValidator._validar_titulo(titulo)
        ProcesoFormativoValidator._validar_observacion(observacion)
        ProcesoFormativoValidator._validar_fechas(fecha_inicio, fecha_fin)
        ProcesoFormativoValidator._validar_idea(idea_id)
        ProcesoFormativoValidator._validar_entidad_externa(entidad_externa_id)
        ProcesoFormativoValidator._validar_palabras_clave(palabras_clave)
        ProcesoFormativoValidator._validar_booleano_opcional(requiere_sustentacion, "requiere_sustentacion")
        ProcesoFormativoValidator._validar_booleano_opcional(permite_segunda_instancia, "permite_segunda_instancia")

    @staticmethod
    def validar_actualizacion(proceso, titulo, observacion, fecha_inicio, fecha_fin, palabras_clave=None):
        ProcesoFormativoValidator._validar_editable(proceso)
        ProcesoFormativoValidator._validar_titulo(titulo, excluir_id=proceso.pk)
        ProcesoFormativoValidator._validar_observacion(observacion)
        ProcesoFormativoValidator._validar_fechas(fecha_inicio, fecha_fin)
        ProcesoFormativoValidator._validar_palabras_clave(palabras_clave)

    @staticmethod
    def validar_calificacion(proceso, aprobado, nota_final=None):
        """Registra el resultado final del proceso (aprobado/reprobado)."""
        if proceso.aprobado is not None:
            raise ValidationError("Este proceso formativo ya fue calificado.")
        if aprobado is None:
            raise ValidationError({"aprobado": "Debe indicar si el proceso fue aprobado o no."})
        if aprobado:
            if nota_final is None:
                raise ValidationError({"nota_final": "La nota final es obligatoria cuando el proceso es aprobado."})
            ProcesoFormativoValidator._validar_nota(nota_final, "nota_final")

    @staticmethod
    def validar_activacion_segunda_instancia(proceso):
        if not proceso.permite_segunda_instancia:
            raise ValidationError("Este proceso no contempla segunda instancia según su flujo.")
        if proceso.segunda_instancia_consumida:
            raise ValidationError("La segunda instancia de este proceso ya fue consumida.")
        if proceso.aprobado is not False:
            raise ValidationError("Solo se puede activar segunda instancia sobre un proceso reprobado.")

    @staticmethod
    def validar_eliminacion(proceso):
        if not proceso.activo:
            raise ValidationError("Este proceso formativo ya se encuentra desactivado.")

    @staticmethod
    def _validar_editable(proceso):
        if proceso.estado_actual == "FINALIZADO":
            raise ValidationError("No se puede editar un proceso formativo ya finalizado.")

    @staticmethod
    def _validar_flujo_version(flujo_version_id):
        if not flujo_version_id:
            raise ValidationError({"flujo_version": "La versión de flujo con la que inicia el proceso es obligatoria."})
        if not FlujoProcesoSelector.existe(flujo_version_id):
            raise ValidationError({"flujo_version": f"No existe un FlujoProceso con id={flujo_version_id}."})

    @staticmethod
    def _validar_titulo(titulo, excluir_id=None):
        if not titulo or not titulo.strip():
            raise ValidationError({"titulo": "El título del proceso formativo es obligatorio."})
        if len(titulo) > TITULO_MAX_LEN:
            raise ValidationError({"titulo": f"El título supera el máximo de {TITULO_MAX_LEN} caracteres."})
        if ProcesoFormativoSelector.existe_titulo(titulo, excluir_id=excluir_id):
            raise ValidationError({"titulo": f"Ya existe un proceso formativo con el título '{titulo}'."})

    @staticmethod
    def _validar_observacion(observacion):
        if not observacion or not observacion.strip():
            raise ValidationError({"observacion": "La observación (tema o área del proyecto) es obligatoria."})

    @staticmethod
    def _validar_fechas(fecha_inicio, fecha_fin):
        if not fecha_inicio or not fecha_fin:
            raise ValidationError("Las fechas de inicio y fin del proceso formativo son obligatorias.")
        if fecha_fin < fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."})

    @staticmethod
    def _validar_idea(idea_id):
        if idea_id is not None and not BancoIdeasSelector.existe(idea_id):
            raise ValidationError({"idea": f"No existe una idea en el Banco de Ideas con id={idea_id}."})

    @staticmethod
    def _validar_entidad_externa(entidad_externa_id):
        if entidad_externa_id is None:
            return
        # Import diferido: crm no es dependencia directa de investigacion_formativa
        from apps.crm.models import EntidadExterna

        if not EntidadExterna.objects.filter(pk=entidad_externa_id).exists():
            raise ValidationError({"entidad_externa": f"No existe una EntidadExterna con id={entidad_externa_id}."})

    @staticmethod
    def _validar_palabras_clave(palabras_clave):
        if palabras_clave and len(palabras_clave) > PALABRAS_CLAVE_MAX_LEN:
            raise ValidationError(
                {"palabras_clave": f"Las palabras clave superan el máximo de {PALABRAS_CLAVE_MAX_LEN} caracteres."}
            )

    @staticmethod
    def _validar_booleano_opcional(valor, campo):
        if valor is not None and not isinstance(valor, bool):
            raise ValidationError({campo: f"El campo '{campo}' debe ser un valor booleano."})

    @staticmethod
    def _validar_nota(nota, campo):
        try:
            valor = float(nota)
        except (TypeError, ValueError):
            raise ValidationError({campo: "La nota debe ser numérica."})
        if valor < 0 or valor > 5:
            raise ValidationError({campo: "La nota debe estar entre 0.0 y 5.0."})