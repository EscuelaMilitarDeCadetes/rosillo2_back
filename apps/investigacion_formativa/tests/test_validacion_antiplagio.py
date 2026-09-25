from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.validacion_antiplagio_service import (
    ValidacionAntiplagioService,
)


class ValidacionAntiplagioServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.documento = self._crear_documento_firma()

    def test_crear_validacion_exitosa(self):
        validacion = ValidacionAntiplagioService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            documento_id=self.documento.pk,
            porcentaje=8.5,
            aprobado=True,
            ejecutor=self.ejecutor,
        )
        self.assertTrue(validacion.aprobado)
        self.assertEqual(validacion.porcentaje, 8.5)

    def test_crear_validacion_duplicada_falla(self):
        ValidacionAntiplagioService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            documento_id=self.documento.pk,
            porcentaje=8.5,
            aprobado=True,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ValidacionAntiplagioService.crear(
                instancia_etapa_id=self.instancia_etapa.pk,
                documento_id=self.documento.pk,
                porcentaje=12.0,
                aprobado=False,
                ejecutor=self.ejecutor,
            )

    def test_crear_validacion_porcentaje_fuera_de_rango_falla(self):
        with self.assertRaises(ValidationError):
            ValidacionAntiplagioService.crear(
                instancia_etapa_id=self.instancia_etapa.pk,
                documento_id=self.documento.pk,
                porcentaje=150,
                aprobado=False,
                ejecutor=self.ejecutor,
            )

    def test_actualizar_validacion_exitoso(self):
        validacion = ValidacionAntiplagioService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            documento_id=self.documento.pk,
            porcentaje=25.0,
            aprobado=False,
            ejecutor=self.ejecutor,
        )
        actualizada = ValidacionAntiplagioService.actualizar(
            validacion_id=validacion.pk, porcentaje=9.0, aprobado=True, ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.porcentaje, 9.0)
        self.assertTrue(actualizada.aprobado)

    def test_listar_por_instancia_etapa(self):
        ValidacionAntiplagioService.crear(
            instancia_etapa_id=self.instancia_etapa.pk,
            documento_id=self.documento.pk,
            porcentaje=8.5,
            aprobado=True,
            ejecutor=self.ejecutor,
        )
        resultado = ValidacionAntiplagioService.listar_por_instancia_etapa(self.instancia_etapa.pk)
        self.assertEqual(resultado.count(), 1)