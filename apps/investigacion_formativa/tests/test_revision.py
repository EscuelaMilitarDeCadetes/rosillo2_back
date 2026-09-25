from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.revision_service import RevisionService


class RevisionServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def test_crear_primera_revision_asigna_version_1(self):
        revision = RevisionService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            observaciones='Falta ajustar el objetivo general.',
            aprobado=False,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(revision.version, 1)

    def test_crear_segunda_revision_incrementa_version(self):
        RevisionService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            observaciones='Primera revisión.',
            aprobado=False,
            ejecutor=self.ejecutor,
        )
        segunda = RevisionService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            observaciones='Segunda revisión, ya corregido.',
            aprobado=True,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(segunda.version, 2)

    def test_crear_revision_sin_observaciones_falla(self):
        with self.assertRaises(ValidationError):
            RevisionService.crear(
                instancia_etapa_id=self.instancia_etapa.pk,
                observaciones='',
                aprobado=True,
                ejecutor=self.ejecutor,
            )

    def test_crear_revision_sin_indicar_aprobado_falla(self):
        with self.assertRaises(ValidationError):
            RevisionService.crear(
                instancia_etapa_id=self.instancia_etapa.pk,
                observaciones='Observación válida',
                aprobado=None,
                ejecutor=self.ejecutor,
            )

    def test_revision_no_expone_actualizar_ni_eliminar(self):
        """Append-only: confirma que el service no ofrece esos métodos."""
        self.assertFalse(hasattr(RevisionService, 'actualizar'))
        self.assertFalse(hasattr(RevisionService, 'eliminar'))

    def test_listar_por_instancia_etapa_ordenado_por_version(self):
        RevisionService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            observaciones='Primera',
            aprobado=False,
            ejecutor=self.ejecutor,
        )
        RevisionService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            observaciones='Segunda',
            aprobado=True,
            ejecutor=self.ejecutor,
        )
        resultado = list(RevisionService.listar_por_instancia_etapa(self.instancia_etapa.pk))
        self.assertEqual(resultado[0].version, 2)
        self.assertEqual(resultado[1].version, 1)