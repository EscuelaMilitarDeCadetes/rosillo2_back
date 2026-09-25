from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.transicion_flujo_service import (
    TransicionFlujoService,
)


class TransicionFlujoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_transicion(self):
        return TransicionFlujoService.crear(
            etapa_origen_id=self.etapa_origen.pk,
            etapa_destino_id=self.etapa_destino.pk,
            nombre='Anteproyecto aprobado',
            ejecutor=self.ejecutor,
        )

    def test_crear_transicion_exitosa(self):
        transicion = self._crear_transicion()
        self.assertTrue(transicion.activo)
        self.assertEqual(transicion.orden, 0)

    def test_crear_transicion_duplicada_falla(self):
        self._crear_transicion()
        with self.assertRaises(ValidationError):
            TransicionFlujoService.crear(
                etapa_origen_id=self.etapa_origen.pk,
                etapa_destino_id=self.etapa_destino.pk,
                nombre='Otro nombre',
                ejecutor=self.ejecutor,
            )

    def test_crear_transicion_sin_nombre_falla(self):
        with self.assertRaises(ValidationError):
            TransicionFlujoService.crear(
                etapa_origen_id=self.etapa_origen.pk,
                etapa_destino_id=self.etapa_destino.pk,
                nombre='',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_transicion_exitoso(self):
        transicion = self._crear_transicion()
        otra_etapa = self._crear_etapa_flujo(
            flujo=self.flujo_transiciones, nombre='Cierre', orden=3, codigo='CIE',
        )
        actualizada = TransicionFlujoService.actualizar(
            transicion_id=transicion.pk,
            etapa_origen_id=self.etapa_origen.pk,
            etapa_destino_id=otra_etapa.pk,
            nombre='Anteproyecto aprobado (v2)',
            ejecutor=self.ejecutor,
            orden=1,
        )
        self.assertEqual(actualizada.etapa_destino_id, otra_etapa.pk)
        self.assertEqual(actualizada.orden, 1)

    def test_desactivar_transicion_exitoso(self):
        transicion = self._crear_transicion()
        desactivada = TransicionFlujoService.desactivar(transicion.pk, ejecutor=self.ejecutor)
        self.assertFalse(desactivada.activo)

    def test_desactivar_transicion_ya_inactiva_falla(self):
        transicion = self._crear_transicion()
        TransicionFlujoService.desactivar(transicion.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            TransicionFlujoService.desactivar(transicion.pk, ejecutor=self.ejecutor)

    def test_activar_transicion_exitoso(self):
        transicion = self._crear_transicion()
        TransicionFlujoService.desactivar(transicion.pk, ejecutor=self.ejecutor)
        activada = TransicionFlujoService.activar(transicion.pk, ejecutor=self.ejecutor)
        self.assertTrue(activada.activo)

    def test_listar_por_etapa_origen(self):
        self._crear_transicion()
        resultado = TransicionFlujoService.listar_por_etapa_origen(self.etapa_origen.pk)
        self.assertEqual(resultado.count(), 1)