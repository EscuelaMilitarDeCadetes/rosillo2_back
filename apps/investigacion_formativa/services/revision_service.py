from django.db import transaction

from apps.investigacion_formativa.models import Revision
from apps.investigacion_formativa.selectors.revision_selector import RevisionSelector
from apps.investigacion_formativa.validators.revision_validator import RevisionValidator
from apps.common.services.historial_service import HistorialService


class RevisionService:
    """Revision es append-only: solo expone listar/obtener/crear (ver
    RevisionValidator y 11_backend_logic.md)."""

    @staticmethod
    def listar():
        return RevisionSelector.listar()

    @staticmethod
    def obtener(revision_id):
        return RevisionSelector.obtener(revision_id)

    @staticmethod
    def listar_por_instancia_etapa(instancia_etapa_id):
        return RevisionSelector.listar_por_instancia_etapa(instancia_etapa_id)

    @staticmethod
    @transaction.atomic
    def crear(instancia_etapa_id, observaciones, aprobado, ejecutor):
        """Calcula automáticamente la siguiente versión consecutiva para la
        instancia de etapa, en vez de exigir que el llamador la adivine."""
        ultima = RevisionSelector.obtener_ultima_por_instancia_etapa(instancia_etapa_id)
        version = 1 if ultima is None else ultima.version + 1

        RevisionValidator.validar_creacion(instancia_etapa_id, version, observaciones, aprobado)

        revision = Revision.objects.create(
            instancia_etapa_id=instancia_etapa_id,
            version=version,
            observaciones=observaciones,
            aprobado=aprobado,
        )
        resultado = "aprobada" if aprobado else "no aprobada"
        HistorialService.registrar(
            ejecutor,
            f"Se registró la revisión v{version} ({resultado}) de la instancia de etapa "
            f"id={instancia_etapa_id} (id revisión={revision.pk}).",
            objeto=revision,
        )
        return revision