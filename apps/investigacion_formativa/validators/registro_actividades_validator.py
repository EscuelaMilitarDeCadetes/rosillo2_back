from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.registro_actividades_selector import (
    RegistroActividadesSelector,
)
from apps.investigacion_formativa.selectors.proceso_formativo_selector import (
    ProcesoFormativoSelector,
)

TIPOS_PERIODO_VALIDOS = {'MENSUAL', 'SEMESTRAL', 'PUNTUAL'}
TIPOS_QUE_REQUIEREN_FECHA_PERIODO = {'MENSUAL', 'SEMESTRAL'}


class RegistroActividadesValidator:

    @staticmethod
    def validar_creacion(proceso_id, registrado_por_id, tipo_periodo, actividades,
                          horas_reportadas=0, fecha_periodo=None, documento_id=None, nota=None):
        RegistroActividadesValidator._validar_proceso(proceso_id)
        RegistroActividadesValidator._validar_registrado_por(registrado_por_id)
        RegistroActividadesValidator._validar_tipo_periodo(tipo_periodo)
        RegistroActividadesValidator._validar_fecha_periodo(tipo_periodo, fecha_periodo)
        RegistroActividadesValidator._validar_actividades(actividades)
        RegistroActividadesValidator._validar_horas_reportadas(horas_reportadas)
        RegistroActividadesValidator._validar_documento(documento_id)
        RegistroActividadesValidator._validar_nota(nota)
        RegistroActividadesValidator._validar_unicidad_registro(proceso_id, registrado_por_id, fecha_periodo)

    @staticmethod
    def validar_actualizacion(registro, tipo_periodo, actividades, horas_reportadas,
                               fecha_periodo=None, documento_id=None, nota=None):
        RegistroActividadesValidator._validar_editable(registro)
        RegistroActividadesValidator._validar_tipo_periodo(tipo_periodo)
        RegistroActividadesValidator._validar_fecha_periodo(tipo_periodo, fecha_periodo)
        RegistroActividadesValidator._validar_actividades(actividades)
        RegistroActividadesValidator._validar_horas_reportadas(horas_reportadas)
        RegistroActividadesValidator._validar_documento(documento_id)
        RegistroActividadesValidator._validar_nota(nota)
        RegistroActividadesValidator._validar_unicidad_registro(
            registro.proceso_id, registro.registrado_por_id, fecha_periodo, excluir_id=registro.pk
        )

    @staticmethod
    def validar_aprobacion(registro):
        if registro.aprobado:
            raise ValidationError("Este registro de actividades ya fue aprobado.")

    @staticmethod
    def validar_eliminacion(registro):
        if not registro.activo:
            raise ValidationError("Este registro de actividades ya se encuentra eliminado.")
        if registro.aprobado:
            raise ValidationError("No se puede eliminar un registro de actividades que ya fue aprobado.")

    @staticmethod
    def _validar_editable(registro):
        if registro.aprobado:
            raise ValidationError("No se puede editar un registro de actividades ya aprobado.")

    @staticmethod
    def _validar_proceso(proceso_id):
        if not proceso_id:
            raise ValidationError({"proceso": "El proceso formativo es obligatorio."})
        if not ProcesoFormativoSelector.existe(proceso_id):
            raise ValidationError({"proceso": f"No existe un ProcesoFormativo con id={proceso_id}."})

    @staticmethod
    def _validar_registrado_por(registrado_por_id):
        if not registrado_por_id:
            raise ValidationError({"registrado_por": "El usuario que registra la actividad es obligatorio."})
        # Import diferido: usuarios no es dependencia directa de investigacion_formativa
        from apps.usuarios.models import Usuario

        if not Usuario.objects.filter(pk=registrado_por_id).exists():
            raise ValidationError({"registrado_por": f"No existe un Usuario con id={registrado_por_id}."})

    @staticmethod
    def _validar_tipo_periodo(tipo_periodo):
        if not tipo_periodo:
            raise ValidationError({"tipo_periodo": "El tipo de período es obligatorio."})
        if tipo_periodo not in TIPOS_PERIODO_VALIDOS:
            raise ValidationError(
                {"tipo_periodo": (
                    f"'{tipo_periodo}' no es un tipo de período válido. "
                    f"Use uno de: {sorted(TIPOS_PERIODO_VALIDOS)}."
                )}
            )

    @staticmethod
    def _validar_fecha_periodo(tipo_periodo, fecha_periodo):
        if tipo_periodo in TIPOS_QUE_REQUIEREN_FECHA_PERIODO and not fecha_periodo:
            raise ValidationError(
                {"fecha_periodo": f"La fecha del período es obligatoria para registros de tipo '{tipo_periodo}'."}
            )

    @staticmethod
    def _validar_actividades(actividades):
        if not actividades or not actividades.strip():
            raise ValidationError({"actividades": "La descripción de las actividades realizadas es obligatoria."})

    @staticmethod
    def _validar_horas_reportadas(horas_reportadas):
        if horas_reportadas is None:
            raise ValidationError({"horas_reportadas": "Las horas reportadas son obligatorias."})
        try:
            valor = float(horas_reportadas)
        except (TypeError, ValueError):
            raise ValidationError({"horas_reportadas": "Las horas reportadas deben ser numéricas."})
        if valor < 0:
            raise ValidationError({"horas_reportadas": "Las horas reportadas no pueden ser negativas."})

    @staticmethod
    def _validar_documento(documento_id):
        if documento_id is None:
            return
        # Import diferido: common no es dependencia directa de investigacion_formativa
        from apps.common.models import DocumentoFirma

        if not DocumentoFirma.objects.filter(pk=documento_id).exists():
            raise ValidationError({"documento": f"No existe un DocumentoFirma con id={documento_id}."})

    @staticmethod
    def _validar_nota(nota):
        if nota is None:
            return
        try:
            valor = float(nota)
        except (TypeError, ValueError):
            raise ValidationError({"nota": "La nota debe ser numérica."})
        if valor < 0 or valor > 5:
            raise ValidationError({"nota": "La nota debe estar entre 0.0 y 5.0."})

    @staticmethod
    def _validar_unicidad_registro(proceso_id, registrado_por_id, fecha_periodo, excluir_id=None):
        if RegistroActividadesSelector.existe_registro(
            proceso_id, registrado_por_id, fecha_periodo, excluir_id=excluir_id
        ):
            raise ValidationError(
                "Ya existe un registro de actividades de este usuario para este proceso "
                "en el mismo período."
            )