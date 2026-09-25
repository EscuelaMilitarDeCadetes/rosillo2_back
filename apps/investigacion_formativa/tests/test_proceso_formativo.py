from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.proceso_formativo_service import (
    ProcesoFormativoService,
)


class ProcesoFormativoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_proceso(self, titulo='Proceso formativo nuevo', permite_segunda_instancia=False):
        return ProcesoFormativoService.crear(
            flujo_version_id=self.flujo.pk,
            titulo=titulo,
            observacion='Observación de prueba',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-06-30',
            ejecutor=self.ejecutor,
            permite_segunda_instancia=permite_segunda_instancia,
        )

    def test_crear_proceso_exitoso(self):
        proceso = self._crear_proceso()
        self.assertTrue(proceso.activo)
        self.assertIsNone(proceso.aprobado)

    def test_crear_proceso_titulo_duplicado_falla(self):
        self._crear_proceso(titulo='Proceso repetido')
        with self.assertRaises(ValidationError):
            self._crear_proceso(titulo='Proceso repetido')

    def test_crear_proceso_fecha_fin_anterior_a_inicio_falla(self):
        with self.assertRaises(ValidationError):
            ProcesoFormativoService.crear(
                flujo_version_id=self.flujo.pk,
                titulo='Proceso con fechas inválidas',
                observacion='Observación',
                fecha_inicio='2025-06-30',
                fecha_fin='2025-01-01',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_proceso_exitoso(self):
        proceso = self._crear_proceso()
        actualizado = ProcesoFormativoService.actualizar(
            proceso_id=proceso.pk,
            titulo='Proceso formativo actualizado',
            observacion='Observación actualizada',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-07-30',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.titulo, 'Proceso formativo actualizado')

    def test_calificar_proceso_aprobado_exitoso(self):
        proceso = self._crear_proceso()
        calificado = ProcesoFormativoService.calificar(
            proceso_id=proceso.pk, aprobado=True, ejecutor=self.ejecutor, nota_final=4.0,
        )
        self.assertTrue(calificado.aprobado)
        self.assertEqual(calificado.nota_final, 4.0)

    def test_calificar_proceso_aprobado_sin_nota_falla(self):
        proceso = self._crear_proceso()
        with self.assertRaises(ValidationError):
            ProcesoFormativoService.calificar(
                proceso_id=proceso.pk, aprobado=True, ejecutor=self.ejecutor,
            )

    def test_calificar_proceso_dos_veces_falla(self):
        proceso = self._crear_proceso()
        ProcesoFormativoService.calificar(
            proceso_id=proceso.pk, aprobado=False, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProcesoFormativoService.calificar(
                proceso_id=proceso.pk, aprobado=True, ejecutor=self.ejecutor, nota_final=4.0,
            )

    def test_activar_segunda_instancia_sin_permitirla_falla(self):
        proceso = self._crear_proceso(permite_segunda_instancia=False)
        ProcesoFormativoService.calificar(
            proceso_id=proceso.pk, aprobado=False, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProcesoFormativoService.activar_segunda_instancia(proceso.pk, ejecutor=self.ejecutor)

    def test_activar_segunda_instancia_reabre_calificacion(self):
        proceso = self._crear_proceso(permite_segunda_instancia=True)
        ProcesoFormativoService.calificar(
            proceso_id=proceso.pk, aprobado=False, ejecutor=self.ejecutor,
        )
        reabierto = ProcesoFormativoService.activar_segunda_instancia(proceso.pk, ejecutor=self.ejecutor)
        self.assertIsNone(reabierto.aprobado)

    def test_eliminar_proceso_soft_delete(self):
        proceso = self._crear_proceso()
        ProcesoFormativoService.eliminar(proceso.pk, ejecutor=self.ejecutor)
        proceso.refresh_from_db()
        self.assertFalse(proceso.activo)

    def test_eliminar_proceso_ya_desactivado_falla(self):
        proceso = self._crear_proceso()
        ProcesoFormativoService.eliminar(proceso.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            ProcesoFormativoService.eliminar(proceso.pk, ejecutor=self.ejecutor)