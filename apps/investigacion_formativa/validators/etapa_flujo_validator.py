# apps/investigacion_formativa/validators/etapa_flujo_validator.py
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.etapa_flujo_selector import EtapaFlujoSelector


class EtapaFlujoValidator:

    TIPOS_ETAPA_VALIDOS = (
        'INICIO', 'CARGA_DOC', 'APROBACION', 'EVALUACION',
        'REVISION', 'SEGUIMIENTO', 'SUSTENTACION', 'CIERRE', 'OTRO',
    )
    ROLES_RESPONSABLE_VALIDOS = ('ESTUDIANTE', 'TUTOR', 'JURADO', 'FACULTAD')

    @staticmethod
    def validar_creacion(flujo_id, nombre, orden, codigo, tipo_etapa, rol_responsable,
                          documento_requerido_id=None, requiere_documento=True,
                          es_final=False, permite_salto=True):
        EtapaFlujoValidator._validar_nombre(nombre)
        EtapaFlujoValidator._validar_orden(orden)
        EtapaFlujoValidator._validar_codigo(codigo)
        EtapaFlujoValidator._validar_tipo_etapa(tipo_etapa)
        EtapaFlujoValidator._validar_rol_responsable(rol_responsable)
        EtapaFlujoValidator._validar_unicidad_orden(flujo_id, orden)
        EtapaFlujoValidator.validar_consistencia_requisitos(documento_requerido_id, requiere_documento)
        EtapaFlujoValidator.validar_etapa_final_no_permite_salto(es_final, permite_salto)

    @staticmethod
    def validar_actualizacion(etapa_id, flujo_id, nombre, orden, codigo, tipo_etapa, rol_responsable,
                               documento_requerido_id=None, requiere_documento=True,
                               es_final=False, permite_salto=True):
        EtapaFlujoValidator._validar_nombre(nombre)
        EtapaFlujoValidator._validar_orden(orden)
        EtapaFlujoValidator._validar_codigo(codigo)
        EtapaFlujoValidator._validar_tipo_etapa(tipo_etapa)
        EtapaFlujoValidator._validar_rol_responsable(rol_responsable)
        EtapaFlujoValidator._validar_unicidad_orden(flujo_id, orden, excluir_id=etapa_id)
        EtapaFlujoValidator.validar_consistencia_requisitos(documento_requerido_id, requiere_documento)
        EtapaFlujoValidator.validar_etapa_final_no_permite_salto(es_final, permite_salto)

    @staticmethod
    def validar_consistencia_requisitos(documento_requerido_id, requiere_documento):
        """Si la etapa exige documento, debe existir un TipoDocumento asociado."""
        if requiere_documento and documento_requerido_id is None:
            raise ValidationError(
                {"documento_requerido": "Esta etapa requiere documento; debe indicar el tipo de documento esperado."}
            )

    @staticmethod
    def validar_etapa_final_no_permite_salto(es_final, permite_salto):
        """Una etapa final no tiene sentido que permita saltar a una etapa posterior."""
        if es_final and permite_salto:
            raise ValidationError(
                {"permite_salto": "Una etapa final no puede permitir salto a una etapa posterior."}
            )

    @staticmethod
    def _validar_nombre(nombre):
        if not nombre or not nombre.strip():
            raise ValidationError({"nombre": "El nombre de la etapa es obligatorio."})
        if len(nombre) > 150:
            raise ValidationError({"nombre": "El nombre supera el máximo de 150 caracteres."})

    @staticmethod
    def _validar_orden(orden):
        if orden is None:
            raise ValidationError({"orden": "El orden de la etapa es obligatorio."})
        try:
            valor = int(orden)
        except (TypeError, ValueError):
            raise ValidationError({"orden": "El orden debe ser un número entero."})
        if valor < 1:
            raise ValidationError({"orden": "El orden debe ser mayor o igual a 1."})

    @staticmethod
    def _validar_codigo(codigo):
        if not codigo or not codigo.strip():
            raise ValidationError({"codigo": "El código de la etapa es obligatorio."})
        if len(codigo) > 100:
            raise ValidationError({"codigo": "El código supera el máximo de 100 caracteres."})

    @staticmethod
    def _validar_tipo_etapa(tipo_etapa):
        if tipo_etapa not in EtapaFlujoValidator.TIPOS_ETAPA_VALIDOS:
            raise ValidationError(
                {"tipo_etapa": f"Tipo de etapa inválido. Debe ser uno de: {', '.join(EtapaFlujoValidator.TIPOS_ETAPA_VALIDOS)}."}
            )

    @staticmethod
    def _validar_rol_responsable(rol_responsable):
        if rol_responsable not in EtapaFlujoValidator.ROLES_RESPONSABLE_VALIDOS:
            raise ValidationError(
                {"rol_responsable": f"Rol responsable inválido. Debe ser uno de: {', '.join(EtapaFlujoValidator.ROLES_RESPONSABLE_VALIDOS)}."}
            )

    @staticmethod
    def _validar_unicidad_orden(flujo_id, orden, excluir_id=None):
        if EtapaFlujoSelector.existe_orden_en_flujo(flujo_id, orden, excluir_id=excluir_id):
            raise ValidationError(
                {"orden": f"Ya existe una etapa con el orden {orden} en este flujo."}
            )