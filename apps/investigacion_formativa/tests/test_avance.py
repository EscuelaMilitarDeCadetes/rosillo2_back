# apps/investigacion_formativa/tests/test_avance.py

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.avance_service import AvanceService


class AvanceServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proceso = self._crear_proceso_formativo()
        self.etapa_1 = self._crear_etapa_flujo(orden=1, nombre='Etapa 1')
        self.etapa_2 = self._crear_etapa_flujo(orden=2, nombre='Etapa 2')

    def test_calcular_avance_por_etapas_sin_instancias(self):
        self.assertEqual(AvanceService.calcular_avance_por_etapas(self.proceso.pk), 0.0)

    def test_calcular_avance_por_etapas_parcial(self):
        self._crear_instancia_etapa(self.proceso, self.etapa_1, estado='APROBADO')
        self._crear_instancia_etapa(self.proceso, self.etapa_2, estado='PENDIENTE')
        self.assertEqual(AvanceService.calcular_avance_por_etapas(self.proceso.pk), 50.0)

    def test_calcular_avance_por_etapas_completo(self):
        self._crear_instancia_etapa(self.proceso, self.etapa_1, estado='APROBADO')
        self._crear_instancia_etapa(self.proceso, self.etapa_2, estado='APROBADO')
        self.assertEqual(AvanceService.calcular_avance_por_etapas(self.proceso.pk), 100.0)

    def test_calcular_avance_tiempo_a_mitad_de_periodo(self):
        hoy = timezone.now().date()
        proceso = self._crear_proceso_formativo(
            titulo='Proceso con tiempo controlado',
            fecha_inicio=hoy - timedelta(days=50),
            fecha_fin=hoy + timedelta(days=50),
        )
        self.assertEqual(AvanceService.calcular_avance_tiempo(proceso.pk), 50.0)

    def test_calcular_avance_tiempo_proceso_vencido_se_limita_a_100(self):
        hoy = timezone.now().date()
        proceso = self._crear_proceso_formativo(
            titulo='Proceso vencido',
            fecha_inicio=hoy - timedelta(days=100),
            fecha_fin=hoy - timedelta(days=10),
        )
        self.assertEqual(AvanceService.calcular_avance_tiempo(proceso.pk), 100.0)

    def test_actualizar_porcentaje_avance_persiste(self):
        self._crear_instancia_etapa(self.proceso, self.etapa_1, estado='APROBADO')
        self._crear_instancia_etapa(self.proceso, self.etapa_2, estado='PENDIENTE')

        actualizado = AvanceService.actualizar_porcentaje_avance(self.proceso.pk, ejecutor=self.ejecutor)

        self.assertEqual(actualizado.porcentaje_avance, 50.0)
        self.proceso.refresh_from_db()
        self.assertEqual(self.proceso.porcentaje_avance, 50.0)