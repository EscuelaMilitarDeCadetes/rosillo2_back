from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.selectors.revision_selector import RevisionSelector
from apps.investigacion_formativa.selectors.instancia_etapa_selector import InstanciaEtapaSelector


class RevisionValidator:
    """Revision es un registro append-only: cada ronda de revisión de una
    InstanciaEtapa genera una nueva versión, nunca se edita ni se borra una
    ya existente (igual que Historial, ver 11_backend_logic.md)."""

    @staticmethod
    def validar_creacion(instancia_etapa_id, version, observaciones, aprobado):
        RevisionValidator._validar_instancia_etapa(instancia_etapa_id)
        RevisionValidator._validar_version(version)
        RevisionValidator._validar_observaciones(observaciones)
        RevisionValidator._validar_aprobado(aprobado)
        RevisionValidator._validar_secuencia_version(instancia_etapa_id, version)
        RevisionValidator._validar_unicidad_version(instancia_etapa_id, version)

    @staticmethod
    def _validar_instancia_etapa(instancia_etapa_id):
        if not instancia_etapa_id:
            raise ValidationError({"instancia_etapa": "La instancia de etapa es obligatoria."})
        if not InstanciaEtapaSelector.existe(instancia_etapa_id):
            raise ValidationError(
                {"instancia_etapa": f"No existe una InstanciaEtapa con id={instancia_etapa_id}."}
            )

    @staticmethod
    def _validar_version(version):
        if version is None:
            raise ValidationError({"version": "El número de versión de la revisión es obligatorio."})
        if not isinstance(version, int) or version < 1:
            raise ValidationError({"version": "La versión debe ser un entero mayor o igual a 1."})

    @staticmethod
    def _validar_observaciones(observaciones):
        if not observaciones or not observaciones.strip():
            raise ValidationError({"observaciones": "Las observaciones de la revisión son obligatorias."})

    @staticmethod
    def _validar_aprobado(aprobado):
        if aprobado is None:
            raise ValidationError({"aprobado": "Debe indicar si la revisión fue aprobada o no."})

    @staticmethod
    def _validar_secuencia_version(instancia_etapa_id, version):
        """La nueva versión debe ser consecutiva a la última revisión registrada."""
        ultima = RevisionSelector.obtener_ultima_por_instancia_etapa(instancia_etapa_id)
        version_esperada = 1 if ultima is None else ultima.version + 1
        if version != version_esperada:
            raise ValidationError(
                {"version": f"La siguiente versión esperada para esta instancia de etapa es {version_esperada}."}
            )

    @staticmethod
    def _validar_unicidad_version(instancia_etapa_id, version):
        if RevisionSelector.existe_version(instancia_etapa_id, version):
            raise ValidationError(
                f"Ya existe una revisión con la versión {version} para esta instancia de etapa."
            )