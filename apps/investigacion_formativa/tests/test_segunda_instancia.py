from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.segunda_instancia_service import (
    SegundaInstanciaService,
)


class SegundaInstanciaServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.etapa_retorno = self.etapa_origen

    def _crear_segunda_instancia(self):
        return SegundaInstanciaService.crear(
            proceso_id=self.proceso.pk,
            instancia_etapa_id=self.instancia_etapa.pk,
            evaluacion_id=self.evaluacion.pk,
            etapa_retorno_id=self.etapa_retorno.pk,
            tipo='TUTOR',
            motivo='El estudiante reprobó por bajo desempeño en el anteproyecto.',
            ejecutor=self.ejecutor,
        )

    def test_crear_segunda_instancia_exitosa(self):
        segunda_instancia = self._crear_segunda_instancia()
        self.assertFalse(segunda_instancia.activada)
        self.assertFalse(segunda_instancia.consumida)
        self.assertTrue(segunda_instancia.activa)
        self.assertEqual(segunda_instancia.nota_maxima, 3.5)

    def test_crear_segunda_instancia_duplicada_para_mismo_proceso_falla(self):
        self._crear_segunda_instancia()
        with self.assertRaises(ValidationError):
            SegundaInstanciaService.crear(
                proceso_id=self.proceso.pk,
                instancia_etapa_id=self.instancia_etapa.pk,
                evaluacion_id=self.evaluacion.pk,
                etapa_retorno_id=self.etapa_retorno.pk,
                tipo='TUTOR',
                motivo='Otro motivo',
                ejecutor=self.ejecutor,
            )

    def test_crear_segunda_instancia_sin_motivo_falla(self):
        with self.assertRaises(ValidationError):
            SegundaInstanciaService.crear(
                proceso_id=self.proceso.pk,
                instancia_etapa_id=self.instancia_etapa.pk,
                evaluacion_id=self.evaluacion.pk,
                etapa_retorno_id=self.etapa_retorno.pk,
                tipo='TUTOR',
                motivo='',
                ejecutor=self.ejecutor,
            )

    def test_activar_segunda_instancia_exitoso(self):
        segunda_instancia = self._crear_segunda_instancia()
        activada = SegundaInstanciaService.activar(segunda_instancia.pk, ejecutor=self.ejecutor)
        self.assertTrue(activada.activada)

    def test_activar_segunda_instancia_ya_activada_falla(self):
        segunda_instancia = self._crear_segunda_instancia()
        SegundaInstanciaService.activar(segunda_instancia.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            SegundaInstanciaService.activar(segunda_instancia.pk, ejecutor=self.ejecutor)

    def test_consumir_sin_activar_falla(self):
        segunda_instancia = self._crear_segunda_instancia()
        with self.assertRaises(ValidationError):
            SegundaInstanciaService.consumir(segunda_instancia.pk, ejecutor=self.ejecutor)

    def test_consumir_segunda_instancia_marca_proceso(self):
        segunda_instancia = self._crear_segunda_instancia()
        SegundaInstanciaService.activar(segunda_instancia.pk, ejecutor=self.ejecutor)
        SegundaInstanciaService.consumir(segunda_instancia.pk, ejecutor=self.ejecutor)

        segunda_instancia.refresh_from_db()
        self.proceso.refresh_from_db()
        self.assertTrue(segunda_instancia.consumida)
        self.assertTrue(self.proceso.segunda_instancia_consumida)

    def test_consumir_dos_veces_falla(self):
        segunda_instancia = self._crear_segunda_instancia()
        SegundaInstanciaService.activar(segunda_instancia.pk, ejecutor=self.ejecutor)
        SegundaInstanciaService.consumir(segunda_instancia.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            SegundaInstanciaService.consumir(segunda_instancia.pk, ejecutor=self.ejecutor)

    def test_eliminar_segunda_instancia_soft_delete(self):
        segunda_instancia = self._crear_segunda_instancia()
        SegundaInstanciaService.eliminar(segunda_instancia.pk, ejecutor=self.ejecutor)
        segunda_instancia.refresh_from_db()
        self.assertFalse(segunda_instancia.activa)

    def test_eliminar_segunda_instancia_ya_desactivada_falla(self):
        segunda_instancia = self._crear_segunda_instancia()
        SegundaInstanciaService.eliminar(segunda_instancia.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            SegundaInstanciaService.eliminar(segunda_instancia.pk, ejecutor=self.ejecutor)