# apps/investigacion_formativa/tests/test_evaluacion_proceso.py

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.evaluacion_proceso_service import EvaluacionProcesoService


class EvaluacionProcesoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proceso = self._crear_proceso_formativo()
        self.etapa = self._crear_etapa_flujo(orden=3, nombre='Etapa evaluable')
        self.instancia = self._crear_instancia_etapa(self.proceso, self.etapa, estado='EN_PROCESO')
        self.tutor = self._crear_participante(self.proceso, rol_en_modalidad='TUTOR')

    def _datos_base(self, **overrides):
        datos = dict(
            evaluador_id=self.tutor.pk,
            instancia_etapa_id=self.instancia.pk,
            concepto='Evaluación de anteproyecto',
            aprobado=True,
            nota=4.5,
            tipo_evaluador='TUTOR',
            tipo_evaluacion='SEGUIMIENTO',
            peso=1.0,
            resultado='APROBADO',
            ejecutor=self.ejecutor,
        )
        datos.update(overrides)
        return datos

    def test_crear_evaluacion_exitosa(self):
        evaluacion = EvaluacionProcesoService.crear(**self._datos_base())
        self.assertEqual(evaluacion.nota, 4.5)
        self.assertTrue(evaluacion.aprobado)

    def test_crear_evaluacion_nota_fuera_de_rango_falla(self):
        with self.assertRaises(ValidationError):
            EvaluacionProcesoService.crear(**self._datos_base(nota=6.0))

    def test_crear_evaluacion_peso_invalido_falla(self):
        with self.assertRaises(ValidationError):
            EvaluacionProcesoService.crear(**self._datos_base(peso=0))

    def test_crear_evaluacion_aprobado_inconsistente_con_nota_falla(self):
        """aprobado=True con nota < 3.5 es inconsistente."""
        with self.assertRaises(ValidationError):
            EvaluacionProcesoService.crear(**self._datos_base(aprobado=True, nota=2.0))

    def test_crear_evaluacion_no_aprobado_con_nota_alta_falla(self):
        """aprobado=False con nota >= 3.5 es inconsistente."""
        with self.assertRaises(ValidationError):
            EvaluacionProcesoService.crear(
                **self._datos_base(aprobado=False, nota=4.0, resultado='NO_APROBADO')
            )

    def test_crear_evaluacion_duplicada_mismo_evaluador_e_instancia_falla(self):
        EvaluacionProcesoService.crear(**self._datos_base())
        with self.assertRaises(ValidationError):
            EvaluacionProcesoService.crear(**self._datos_base(concepto='Segundo intento'))

    def test_crear_evaluacion_resultado_vacio_falla(self):
        with self.assertRaises(ValidationError):
            EvaluacionProcesoService.crear(**self._datos_base(resultado=''))

    def test_listar_por_instancia_etapa(self):
        EvaluacionProcesoService.crear(**self._datos_base())
        evaluaciones = EvaluacionProcesoService.listar_por_instancia_etapa(self.instancia.pk)
        self.assertEqual(evaluaciones.count(), 1)