from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector
from apps.investigacion_formal.selectors.monto_selector import MontoSelector


class MontoValidator:

    @staticmethod
    def validar_creacion(proyecto_id, solicitado):
        MontoValidator._validar_proyecto(proyecto_id)
        MontoValidator._validar_solicitado(solicitado)
        MontoValidator._validar_unicidad_proyecto(proyecto_id)

    @staticmethod
    def validar_asignacion(aprobado, contrapartida):
        """Reglas para cuando cinternos/cexternos asignan el monto aprobado."""
        MontoValidator._validar_valor_no_negativo(aprobado, "aprobado")
        MontoValidator._validar_valor_no_negativo(contrapartida, "contrapartida")

    @staticmethod
    def validar_edicion_gasto(monto, nuevo_aprobado):
        """Réplica de editarMontoXProyecto: no permitir bajar el aprobado por debajo
        de lo ya ejecutado."""
        MontoValidator._validar_valor_no_negativo(nuevo_aprobado, "aprobado")
        ejecutado = monto.ejecutado or 0
        if nuevo_aprobado < ejecutado:
            raise ValidationError(
                {"aprobado": (
                    f"El nuevo valor aprobado ({nuevo_aprobado}) no puede ser menor "
                    f"al valor ya ejecutado ({ejecutado})."
                )}
            )
    
    @staticmethod
    def validar_contrapartida(contrapartida):
        if contrapartida is None:
            raise ValidationError({"contrapartida": "La contrapartida es obligatoria."})
        MontoValidator._validar_valor_no_negativo(contrapartida, "contrapartida")

    @staticmethod
    def _validar_proyecto(proyecto_id):
        if not proyecto_id:
            raise ValidationError({"proyecto": "El proyecto es obligatorio."})
        if not ProyectoSelector.existe(proyecto_id):
            raise ValidationError({"proyecto": f"No existe un Proyecto con id={proyecto_id}."})

    @staticmethod
    def _validar_solicitado(solicitado):
        MontoValidator._validar_valor_no_negativo(solicitado, "solicitado")

    @staticmethod
    def _validar_valor_no_negativo(valor, campo):
        if valor is None:
            return
        try:
            monto_valor = float(valor)
        except (TypeError, ValueError):
            raise ValidationError({campo: f"El valor de '{campo}' debe ser numérico."})
        if monto_valor < 0:
            raise ValidationError({campo: f"El valor de '{campo}' no puede ser negativo."})

    @staticmethod
    def _validar_unicidad_proyecto(proyecto_id, excluir_id=None):
        if MontoSelector.existe_para_proyecto(proyecto_id, excluir_id=excluir_id):
            raise ValidationError(
                "Este proyecto ya tiene un registro de monto asociado."
            )