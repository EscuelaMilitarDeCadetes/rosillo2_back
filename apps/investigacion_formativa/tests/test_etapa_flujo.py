# apps/investigacion_formativa/tests/test_etapa_flujo.py

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.etapa_flujo_service import EtapaFlujoService


class EtapaFlujoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def test_crear_etapa_exitosa(self):
        etapa = EtapaFlujoService.crear(
            flujo_id=self.flujo.pk,
            nombre='Anteproyecto',
            orden=1,
            codigo='ANT-01',
            rol_responsable='ESTUDIANTE',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(etapa.orden, 1)
        self.assertEqual(etapa.tipo_etapa, 'OTRO')

    def test_crear_etapa_orden_duplicado_en_mismo_flujo_falla(self):
        EtapaFlujoService.crear(
            flujo_id=self.flujo.pk, nombre='Anteproyecto', orden=1,
            codigo='ANT-01', rol_responsable='ESTUDIANTE', ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EtapaFlujoService.crear(
                flujo_id=self.flujo.pk, nombre='Otra etapa', orden=1,
                codigo='OTR-01', rol_responsable='TUTOR', ejecutor=self.ejecutor,
            )

    def test_crear_etapa_rol_responsable_invalido_falla(self):
        with self.assertRaises(ValidationError):
            EtapaFlujoService.crear(
                flujo_id=self.flujo.pk, nombre='Etapa inválida', orden=1,
                codigo='INV-01', rol_responsable='DECANO', ejecutor=self.ejecutor,
            )

    def test_crear_etapa_orden_menor_a_uno_falla(self):
        with self.assertRaises(ValidationError):
            EtapaFlujoService.crear(
                flujo_id=self.flujo.pk, nombre='Etapa inválida', orden=0,
                codigo='INV-02', rol_responsable='ESTUDIANTE', ejecutor=self.ejecutor,
            )

    def test_actualizar_etapa_exitosa(self):
        etapa = EtapaFlujoService.crear(
            flujo_id=self.flujo.pk, nombre='Anteproyecto', orden=1,
            codigo='ANT-01', rol_responsable='ESTUDIANTE', ejecutor=self.ejecutor,
        )
        actualizada = EtapaFlujoService.actualizar(
            etapa_id=etapa.pk, nombre='Anteproyecto revisado', orden=1,
            codigo='ANT-01', rol_responsable='TUTOR', ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.nombre, 'Anteproyecto revisado')
        self.assertEqual(actualizada.rol_responsable, 'TUTOR')

    def test_actualizar_etapa_orden_duplicado_con_otra_etapa_falla(self):
        EtapaFlujoService.crear(
            flujo_id=self.flujo.pk, nombre='Etapa 1', orden=1,
            codigo='ETP-01', rol_responsable='ESTUDIANTE', ejecutor=self.ejecutor,
        )
        etapa_2 = EtapaFlujoService.crear(
            flujo_id=self.flujo.pk, nombre='Etapa 2', orden=2,
            codigo='ETP-02', rol_responsable='TUTOR', ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EtapaFlujoService.actualizar(
                etapa_id=etapa_2.pk, nombre='Etapa 2 renombrada', orden=1,
                codigo='ETP-02', rol_responsable='TUTOR', ejecutor=self.ejecutor,
            )

    def test_actualizar_etapa_mismo_orden_no_falla(self):
        """Actualizar sin cambiar el orden no debe chocar consigo misma."""
        etapa = EtapaFlujoService.crear(
            flujo_id=self.flujo.pk, nombre='Etapa única', orden=1,
            codigo='ETP-01', rol_responsable='ESTUDIANTE', ejecutor=self.ejecutor,
        )
        actualizada = EtapaFlujoService.actualizar(
            etapa_id=etapa.pk, nombre='Etapa única renombrada', orden=1,
            codigo='ETP-01', rol_responsable='ESTUDIANTE', ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.nombre, 'Etapa única renombrada')

    def test_listar_por_flujo(self):
        EtapaFlujoService.crear(
            flujo_id=self.flujo.pk, nombre='Etapa 1', orden=1,
            codigo='ETP-01', rol_responsable='ESTUDIANTE', ejecutor=self.ejecutor,
        )
        EtapaFlujoService.crear(
            flujo_id=self.flujo.pk, nombre='Etapa 2', orden=2,
            codigo='ETP-02', rol_responsable='TUTOR', ejecutor=self.ejecutor,
        )
        etapas = EtapaFlujoService.listar_por_flujo(self.flujo.pk)
        self.assertEqual(etapas.count(), 2)