from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.flujo_proceso_service import FlujoProcesoService


class FlujoProcesoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_flujo(self, nombre='Flujo alterno TG', version=3):
        return FlujoProcesoService.crear(
            modalidad_id=self.modalidad.pk,
            nombre=nombre,
            fecha_vigencia_inicio=timezone.now().date(),
            ejecutor=self.ejecutor,
            version=version,
        )

    def test_crear_flujo_exitoso(self):
        flujo = self._crear_flujo()
        self.assertTrue(flujo.activo)
        self.assertEqual(flujo.tipo, 'FORMATIVA')

    def test_crear_flujo_version_duplicada_para_modalidad_falla(self):
        # self.flujo (fixture base) ya usa modalidad=self.modalidad, version=1
        with self.assertRaises(ValidationError):
            FlujoProcesoService.crear(
                modalidad_id=self.modalidad.pk,
                nombre='Otro flujo',
                fecha_vigencia_inicio=timezone.now().date(),
                ejecutor=self.ejecutor,
                version=1,
            )

    def test_crear_flujo_sin_nombre_falla(self):
        with self.assertRaises(ValidationError):
            FlujoProcesoService.crear(
                modalidad_id=self.modalidad.pk,
                nombre='',
                fecha_vigencia_inicio=timezone.now().date(),
                ejecutor=self.ejecutor,
                version=2,
            )

    def test_actualizar_flujo_exitoso(self):
        flujo = self._crear_flujo()
        actualizado = FlujoProcesoService.actualizar(
            flujo_id=flujo.pk,
            nombre='Flujo alterno TG (revisado)',
            fecha_vigencia_inicio=timezone.now().date(),
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.nombre, 'Flujo alterno TG (revisado)')

    def test_eliminar_flujo_soft_delete(self):
        flujo = self._crear_flujo()
        FlujoProcesoService.eliminar(flujo.pk, ejecutor=self.ejecutor)
        flujo.refresh_from_db()
        self.assertFalse(flujo.activo)

    def test_activar_flujo_exitoso(self):
        flujo = self._crear_flujo()
        FlujoProcesoService.eliminar(flujo.pk, ejecutor=self.ejecutor)
        activado = FlujoProcesoService.activar(flujo.pk, ejecutor=self.ejecutor)
        self.assertTrue(activado.activo)

    def test_listar_por_modalidad(self):
        self._crear_flujo()
        resultado = FlujoProcesoService.listar_por_modalidad(self.modalidad.pk)
        # self.flujo (fixture base) + el nuevo creado en este test
        self.assertEqual(resultado.count(), 3)

    def test_listar_activos_excluye_desactivados(self):
        flujo = self._crear_flujo()
        FlujoProcesoService.eliminar(flujo.pk, ejecutor=self.ejecutor)
        resultado = FlujoProcesoService.listar_activos()
        self.assertNotIn(flujo.pk, [f.pk for f in resultado])