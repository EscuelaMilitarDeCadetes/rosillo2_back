from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.models import RegistroActividades
from apps.investigacion_formativa.services.registro_horas_service import RegistroHorasService


class RegistroHorasServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_registro_actividades(self, horas_reportadas=40):
        return RegistroActividades.objects.create(
            proceso=self.proceso,
            registrado_por=self.ejecutor,
            tipo_periodo='PUNTUAL',
            actividades='Actividades de prueba',
            horas_reportadas=horas_reportadas,
        )

    def test_crear_control_horas_exitoso(self):
        control = RegistroHorasService.crear(
            proceso_id=self.proceso.pk, ejecutor=self.ejecutor,
        )
        self.assertEqual(control.horas_requeridas, 120)
        self.assertEqual(control.horas_acumuladas, 0)
        self.assertFalse(control.cumple_requisito)

    def test_crear_control_horas_duplicado_para_proceso_falla(self):
        RegistroHorasService.crear(proceso_id=self.proceso.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            RegistroHorasService.crear(proceso_id=self.proceso.pk, ejecutor=self.ejecutor)

    def test_crear_control_horas_requeridas_invalidas_falla(self):
        with self.assertRaises(ValidationError):
            RegistroHorasService.crear(
                proceso_id=self.proceso.pk, ejecutor=self.ejecutor, horas_requeridas=0,
            )

    def test_ajustar_horas_requeridas_exitoso(self):
        control = RegistroHorasService.crear(proceso_id=self.proceso.pk, ejecutor=self.ejecutor)
        ajustado = RegistroHorasService.ajustar_horas_requeridas(
            registro_horas_id=control.pk, nuevas_horas_requeridas=100, ejecutor=self.ejecutor,
        )
        self.assertEqual(ajustado.horas_requeridas, 100)

    def test_ajustar_horas_requeridas_por_debajo_de_acumuladas_falla(self):
        control = RegistroHorasService.crear(proceso_id=self.proceso.pk, ejecutor=self.ejecutor)
        self._crear_registro_actividades(horas_reportadas=50)
        RegistroHorasService.recalcular(control.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            RegistroHorasService.ajustar_horas_requeridas(
                registro_horas_id=control.pk, nuevas_horas_requeridas=30, ejecutor=self.ejecutor,
            )

    def test_recalcular_control_horas_suma_registros_actividades(self):
        control = RegistroHorasService.crear(
            proceso_id=self.proceso.pk, ejecutor=self.ejecutor, horas_requeridas=60,
        )
        self._crear_registro_actividades(horas_reportadas=40)
        self._crear_registro_actividades(horas_reportadas=25)
        recalculado = RegistroHorasService.recalcular(control.pk, ejecutor=self.ejecutor)
        self.assertEqual(recalculado.horas_acumuladas, 65)
        self.assertTrue(recalculado.cumple_requisito)

    def test_obtener_por_proceso(self):
        RegistroHorasService.crear(proceso_id=self.proceso.pk, ejecutor=self.ejecutor)
        control = RegistroHorasService.obtener_por_proceso(self.proceso.pk)
        self.assertIsNotNone(control)
        self.assertEqual(control.proceso_id, self.proceso.pk)