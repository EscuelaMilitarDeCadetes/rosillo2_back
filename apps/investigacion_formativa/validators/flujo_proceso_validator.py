# apps/investigacion_formativa/validators/flujo_proceso_validator.py

from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.flujo_proceso_selector import FlujoProcesoSelector

TIPOS_VALIDOS = ('FORMATIVA', 'FORMAL')


class FlujoProcesoValidator:

    @staticmethod
    def validar_creacion(modalidad_id, nombre, fecha_vigencia_inicio, version, tipo, descripcion, fecha_vigencia_fin):
        FlujoProcesoValidator._validar_nombre(nombre)
        FlujoProcesoValidator._validar_version(version)
        FlujoProcesoValidator._validar_tipo(tipo)
        FlujoProcesoValidator._validar_vigencia(fecha_vigencia_inicio, fecha_vigencia_fin)
        FlujoProcesoValidator._validar_unicidad_nombre(nombre)
        FlujoProcesoValidator._validar_unicidad_version(modalidad_id, version)

    @staticmethod
    def validar_actualizacion(flujo, nombre, fecha_vigencia_inicio, descripcion, fecha_vigencia_fin):
        # El service solo actualiza nombre/descripcion/fechas; modalidad y version
        # no cambian tras la creación, así que aquí no se revalidan.
        FlujoProcesoValidator._validar_nombre(nombre)
        FlujoProcesoValidator._validar_vigencia(fecha_vigencia_inicio, fecha_vigencia_fin)
        FlujoProcesoValidator._validar_unicidad_nombre(nombre, excluir_id=flujo.pk)

    @staticmethod
    def validar_activacion(flujo):
        if flujo.activo:
            raise ValidationError("Este flujo ya se encuentra activo.")

    @staticmethod
    def validar_eliminacion(flujo):
        if not flujo.activo:
            raise ValidationError("Este flujo ya se encuentra inactivo.")

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre del flujo es obligatorio."})
        if len(nombre) > 150:
            raise ValidationError({"nombre": "El nombre supera el máximo de caracteres permitido."})

    @staticmethod
    def _validar_version(version):
        if version is None:
            raise ValidationError({"version": "La versión del flujo es obligatoria."})
        try:
            valor = int(version)
        except (TypeError, ValueError):
            raise ValidationError({"version": "La versión debe ser un número entero."})
        if valor < 1:
            raise ValidationError({"version": "La versión debe ser mayor o igual a 1."})

    @staticmethod
    def _validar_tipo(tipo):
        if tipo not in TIPOS_VALIDOS:
            raise ValidationError(
                {"tipo": f"Tipo inválido. Debe ser uno de: {', '.join(TIPOS_VALIDOS)}."}
            )

    @staticmethod
    def _validar_vigencia(fecha_vigencia_inicio, fecha_vigencia_fin):
        if not fecha_vigencia_inicio:
            raise ValidationError({"fecha_vigencia_inicio": "La fecha de inicio de vigencia es obligatoria."})
        if fecha_vigencia_fin and fecha_vigencia_fin < fecha_vigencia_inicio:
            raise ValidationError(
                {"fecha_vigencia_fin": "La fecha de fin de vigencia no puede ser anterior a la de inicio."}
            )

    @staticmethod
    def _validar_unicidad_nombre(nombre, excluir_id=None):
        if FlujoProcesoSelector.existe_nombre(nombre, excluir_id=excluir_id):
            raise ValidationError({"nombre": f"Ya existe un flujo con el nombre '{nombre}'."})

    @staticmethod
    def _validar_unicidad_version(modalidad_id, version, excluir_id=None):
        if FlujoProcesoSelector.existe_version_en_modalidad(modalidad_id, version, excluir_id=excluir_id):
            raise ValidationError(
                {"version": f"Ya existe la versión {version} del flujo para esta modalidad."}
            )