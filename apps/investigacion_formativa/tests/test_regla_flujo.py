from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.regla_flujo_service import ReglaFlujoService


class ReglaFlujoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_regla(self, nombre='Nota mínima anteproyecto'):
        return ReglaFlujoService.crear(
            etapa_origen_id=self.etapa_origen.pk,
            etapa_destino_id=self.etapa_destino.pk,
            nombre=nombre,
            operador='GTE',
            tipo_regla='NOTA_MINIMA',
            valor_minimo=3.0,
            valor_maximo=5.0,
            mensaje_error='La nota debe ser mayor o igual a 3.0',
            accion_resultado='AVANZAR',
            descripcion='Regla de prueba',
            fecha_inicio=timezone.now(),
            ejecutor=self.ejecutor,
        )

    def test_crear_regla_exitosa(self):
        regla = self._crear_regla()
        self.assertTrue(regla.activa)
        self.assertEqual(regla.prioridad, 1)

    def test_crear_regla_duplicada_falla(self):
        self._crear_regla()
        with self.assertRaises(ValidationError):
            self._crear_regla()

    def test_crear_regla_valor_maximo_menor_a_minimo_falla(self):
        with self.assertRaises(ValidationError):
            ReglaFlujoService.crear(
                etapa_origen_id=self.etapa_origen.pk,
                etapa_destino_id=self.etapa_destino.pk,
                nombre='Regla inválida',
                operador='GTE',
                tipo_regla='NOTA_MINIMA',
                valor_minimo=5.0,
                valor_maximo=3.0,
                mensaje_error='Mensaje',
                accion_resultado='AVANZAR',
                descripcion='Descripción',
                fecha_inicio=timezone.now(),
                ejecutor=self.ejecutor,
            )

    def test_crear_regla_operador_invalido_falla(self):
        with self.assertRaises(ValidationError):
            ReglaFlujoService.crear(
                etapa_origen_id=self.etapa_origen.pk,
                etapa_destino_id=self.etapa_destino.pk,
                nombre='Regla inválida',
                operador='DISTINTO_DE',
                tipo_regla='NOTA_MINIMA',
                valor_minimo=3.0,
                valor_maximo=5.0,
                mensaje_error='Mensaje',
                accion_resultado='AVANZAR',
                descripcion='Descripción',
                fecha_inicio=timezone.now(),
                ejecutor=self.ejecutor,
            )

    def test_actualizar_regla_exitoso(self):
        regla = self._crear_regla()
        actualizada = ReglaFlujoService.actualizar(
            regla_id=regla.pk,
            etapa_origen_id=self.etapa_origen.pk,
            etapa_destino_id=self.etapa_destino.pk,
            nombre='Nota mínima anteproyecto (v2)',
            operador='GTE',
            tipo_regla='NOTA_MINIMA',
            valor_minimo=3.5,
            valor_maximo=5.0,
            mensaje_error='La nota debe ser mayor o igual a 3.5',
            accion_resultado='AVANZAR',
            descripcion='Descripción actualizada',
            fecha_inicio=timezone.now(),
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.valor_minimo, 3.5)

    def test_desactivar_y_activar_regla(self):
        regla = self._crear_regla()
        ReglaFlujoService.desactivar(regla.pk, ejecutor=self.ejecutor)
        regla.refresh_from_db()
        self.assertFalse(regla.activa)

        ReglaFlujoService.activar(regla.pk, ejecutor=self.ejecutor)
        regla.refresh_from_db()
        self.assertTrue(regla.activa)

    def test_activar_regla_ya_activa_falla(self):
        regla = self._crear_regla()
        with self.assertRaises(ValidationError):
            ReglaFlujoService.activar(regla.pk, ejecutor=self.ejecutor)

    def test_listar_por_transicion(self):
        self._crear_regla()
        resultado = ReglaFlujoService.listar_por_transicion(self.etapa_origen.pk, self.etapa_destino.pk)
        self.assertEqual(resultado.count(), 1)