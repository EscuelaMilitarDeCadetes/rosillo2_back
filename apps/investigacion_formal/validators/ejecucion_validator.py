from rest_framework.exceptions import ValidationError

from apps.investigacion_formal.selectors.monto_selector import MontoSelector
from apps.investigacion_formal.selectors.tipo_rubro_selector import TipoRubroSelector


class EjecucionValidator:

    @staticmethod
    def validar_creacion(monto_id, tipo_rubro_id, nombre, costo, descripcion):
        EjecucionValidator._validar_monto(monto_id)
        EjecucionValidator._validar_tipo_rubro(tipo_rubro_id)
        EjecucionValidator._validar_nombre(nombre)
        EjecucionValidator._validar_costo(costo)
        EjecucionValidator._validar_descripcion(descripcion)
        EjecucionValidator._validar_no_exceder_presupuesto(monto_id, costo)

    @staticmethod
    def validar_actualizacion(ejecucion, monto_id, tipo_rubro_id, nombre, costo, descripcion):
        EjecucionValidator._validar_monto(monto_id)
        monto_actual = MontoSelector.obtener(ejecucion.monto_id)
        nuevo_monto = MontoSelector.obtener(monto_id)
        if monto_actual.proyecto_id != nuevo_monto.proyecto_id:
            raise ValidationError({
                "monto": (
                    "La ejecución no puede cambiarse a un monto "
                    "perteneciente a otro proyecto."
                )
            })
        EjecucionValidator._validar_tipo_rubro(tipo_rubro_id)
        EjecucionValidator._validar_nombre(nombre)
        EjecucionValidator._validar_costo(costo)
        EjecucionValidator._validar_descripcion(descripcion)
        diferencia = costo - ejecucion.costo
        if diferencia > 0:
            EjecucionValidator._validar_no_exceder_presupuesto(
                monto_id, diferencia
            )

    @staticmethod
    def validar_eliminacion(ejecucion):
        if not ejecucion.estado:
            raise ValidationError("Esta ejecución ya se encuentra desactivada.")

    @staticmethod
    def _validar_monto(monto_id):
        if not monto_id:
            raise ValidationError({"monto": "El monto asociado es obligatorio."})
        if not MontoSelector.existe(monto_id):
            raise ValidationError({"monto": f"No existe un Monto con id={monto_id}."})

    @staticmethod
    def _validar_tipo_rubro(tipo_rubro_id):
        if not tipo_rubro_id:
            raise ValidationError({"tipo_rubro": "El tipo de rubro es obligatorio."})
        if not TipoRubroSelector.existe(tipo_rubro_id):
            raise ValidationError({"tipo_rubro": f"No existe un TipoRubro con id={tipo_rubro_id}."})

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre del gasto es obligatorio."})
        if len(nombre) > 255:
            raise ValidationError({"nombre": "El nombre supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_costo(costo):
        if costo is None:
            raise ValidationError({"costo": "El costo es obligatorio."})
        try:
            valor = float(costo)
        except (TypeError, ValueError):
            raise ValidationError({"costo": "El costo debe ser numérico."})
        if valor < 0:
            raise ValidationError({"costo": "El costo no puede ser negativo."})

    @staticmethod
    def _validar_descripcion(descripcion):
        if not descripcion or not descripcion.strip():
            raise ValidationError({"descripcion": "La descripción del gasto es obligatoria."})
        if len(descripcion) > 255:
            raise ValidationError({"descripcion": "La descripción supera el máximo de 255 caracteres."})

    @staticmethod
    def _validar_no_exceder_presupuesto(monto_id, costo_adicional):
        monto = MontoSelector.buscar(monto_id)
        if monto is None:
            return
        ejecutado = monto.ejecutado or 0
        aprobado = monto.aprobado or 0
        if (ejecutado + costo_adicional) > aprobado:
            raise ValidationError(
                f"El gasto de {costo_adicional} excede el monto aprobado disponible "
                f"para este proyecto (ejecutado={ejecutado}, aprobado={aprobado})."
            )