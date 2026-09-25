from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.plan_trabajo_service import PlanTrabajoService


class PlanTrabajoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_plan(self):
        return PlanTrabajoService.crear(
            proceso_id=self.proceso.pk,
            descripcion_general='Descripción general del plan de trabajo.',
            objetivo_general='Diseñar e implementar un prototipo funcional.',
            actividades_planeadas='Revisión bibliográfica, diseño, implementación, pruebas.',
            fecha_inicio_planeada='2025-01-15',
            fecha_fin_planeada='2025-06-15',
            ejecutor=self.ejecutor,
        )

    def test_crear_plan_exitoso(self):
        plan = self._crear_plan()
        self.assertEqual(plan.estado, 'BORRADOR')

    def test_crear_segundo_plan_para_mismo_proceso_falla(self):
        self._crear_plan()
        with self.assertRaises(ValidationError):
            self._crear_plan()

    def test_crear_plan_fecha_fin_anterior_a_inicio_falla(self):
        with self.assertRaises(ValidationError):
            PlanTrabajoService.crear(
                proceso_id=self.proceso.pk,
                descripcion_general='Descripción',
                objetivo_general='Objetivo',
                actividades_planeadas='Actividades',
                fecha_inicio_planeada='2025-06-15',
                fecha_fin_planeada='2025-01-15',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_plan_en_borrador_exitoso(self):
        plan = self._crear_plan()
        actualizado = PlanTrabajoService.actualizar(
            plan_trabajo_id=plan.pk,
            descripcion_general='Descripción actualizada',
            objetivo_general=plan.objetivo_general,
            actividades_planeadas=plan.actividades_planeadas,
            fecha_inicio_planeada='2025-01-15',
            fecha_fin_planeada='2025-06-15',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.descripcion_general, 'Descripción actualizada')

    def test_actualizar_plan_enviado_falla(self):
        plan = self._crear_plan()
        PlanTrabajoService.enviar(plan.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            PlanTrabajoService.actualizar(
                plan_trabajo_id=plan.pk,
                descripcion_general='Intento de edición',
                objetivo_general=plan.objetivo_general,
                actividades_planeadas=plan.actividades_planeadas,
                fecha_inicio_planeada='2025-01-15',
                fecha_fin_planeada='2025-06-15',
                ejecutor=self.ejecutor,
            )

    def test_flujo_completo_enviar_y_aprobar(self):
        plan = self._crear_plan()
        PlanTrabajoService.enviar(plan.pk, ejecutor=self.ejecutor)
        aprobado = PlanTrabajoService.aprobar(
            plan_trabajo_id=plan.pk, aprobado_por_id=self.ejecutor.pk, ejecutor=self.ejecutor,
        )
        self.assertEqual(aprobado.estado, 'APROBADO')
        self.assertIsNotNone(aprobado.fecha_aprobacion)
        self.assertEqual(aprobado.aprobado_por_id, self.ejecutor.pk)

    def test_aprobar_plan_en_borrador_falla(self):
        plan = self._crear_plan()
        with self.assertRaises(ValidationError):
            PlanTrabajoService.aprobar(
                plan_trabajo_id=plan.pk, aprobado_por_id=self.ejecutor.pk, ejecutor=self.ejecutor,
            )

    def test_rechazar_plan_enviado_exitoso(self):
        plan = self._crear_plan()
        PlanTrabajoService.enviar(plan.pk, ejecutor=self.ejecutor)
        rechazado = PlanTrabajoService.rechazar(
            plan_trabajo_id=plan.pk,
            observaciones='Falta profundidad en la metodología.',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(rechazado.estado, 'RECHAZADO')

    def test_rechazar_plan_sin_observaciones_falla(self):
        plan = self._crear_plan()
        PlanTrabajoService.enviar(plan.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            PlanTrabajoService.rechazar(
                plan_trabajo_id=plan.pk, observaciones='', ejecutor=self.ejecutor,
            )

    def test_eliminar_plan_enviado_falla(self):
        plan = self._crear_plan()
        PlanTrabajoService.enviar(plan.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            PlanTrabajoService.eliminar(plan.pk, ejecutor=self.ejecutor)

    def test_obtener_por_proceso(self):
        plan = self._crear_plan()
        encontrado = PlanTrabajoService.obtener_por_proceso(self.proceso.pk)
        self.assertEqual(encontrado.pk, plan.pk)