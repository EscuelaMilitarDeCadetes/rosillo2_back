from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.registro_actividades_service import (
    RegistroActividadesService,
)
from apps.investigacion_formativa.services.registro_horas_service import RegistroHorasService


class RegistroActividadesServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_registro(self, tipo_periodo='PUNTUAL', horas_reportadas=10, fecha_periodo=None):
        return RegistroActividadesService.crear(
            proceso_id=self.proceso.pk,
            registrado_por_id=self.ejecutor.pk,
            tipo_periodo=tipo_periodo,
            actividades='Revisión de literatura sobre el tema del anteproyecto.',
            ejecutor=self.ejecutor,
            horas_reportadas=horas_reportadas,
            fecha_periodo=fecha_periodo,
        )

    def test_crear_registro_puntual_exitoso(self):
        registro = self._crear_registro()
        self.assertFalse(registro.aprobado)
        self.assertEqual(registro.horas_reportadas, 10)

    def test_crear_registro_mensual_sin_fecha_periodo_falla(self):
        with self.assertRaises(ValidationError):
            self._crear_registro(tipo_periodo='MENSUAL', fecha_periodo=None)

    def test_crear_registro_mensual_con_fecha_periodo_exitoso(self):
        registro = self._crear_registro(tipo_periodo='MENSUAL', fecha_periodo='2025-02-01')
        self.assertEqual(registro.tipo_periodo, 'MENSUAL')

    def test_crear_registro_horas_negativas_falla(self):
        with self.assertRaises(ValidationError):
            self._crear_registro(horas_reportadas=-5)

    def test_actualizar_registro_no_aprobado_exitoso(self):
        registro = self._crear_registro(horas_reportadas=10)
        actualizado = RegistroActividadesService.actualizar(
            registro_id=registro.pk,
            tipo_periodo='PUNTUAL',
            actividades='Actividades actualizadas',
            horas_reportadas=15,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.horas_reportadas, 15)

    def test_actualizar_registro_aprobado_falla(self):
        registro = self._crear_registro()
        RegistroActividadesService.aprobar(registro.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            RegistroActividadesService.actualizar(
                registro_id=registro.pk,
                tipo_periodo='PUNTUAL',
                actividades='Intento de edición',
                horas_reportadas=20,
                ejecutor=self.ejecutor,
            )

    def test_aprobar_registro_recalcula_control_horas(self):
        control = RegistroHorasService.crear(
            proceso_id=self.proceso.pk, ejecutor=self.ejecutor, horas_requeridas=20,
        )
        registro = self._crear_registro(horas_reportadas=25)
        RegistroActividadesService.aprobar(registro.pk, ejecutor=self.ejecutor)

        control.refresh_from_db()
        self.assertEqual(control.horas_acumuladas, 25)
        self.assertTrue(control.cumple_requisito)

    def test_aprobar_registro_dos_veces_falla(self):
        registro = self._crear_registro()
        RegistroActividadesService.aprobar(registro.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            RegistroActividadesService.aprobar(registro.pk, ejecutor=self.ejecutor)

    def test_eliminar_registro_no_aprobado_exitoso(self):
        registro = self._crear_registro()
        pk = registro.pk
        RegistroActividadesService.eliminar(pk, ejecutor=self.ejecutor)
        self.assertFalse(RegistroActividadesService.listar().filter(pk=pk).exists())

    def test_eliminar_registro_aprobado_falla(self):
        registro = self._crear_registro()
        RegistroActividadesService.aprobar(registro.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            RegistroActividadesService.eliminar(registro.pk, ejecutor=self.ejecutor)

    def test_listar_por_proceso(self):
        self._crear_registro()
        resultado = RegistroActividadesService.listar_por_proceso(self.proceso.pk)
        self.assertEqual(resultado.count(), 1)