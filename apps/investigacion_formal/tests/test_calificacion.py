from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.calificacion_service import CalificacionService


class CalificacionServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proyecto_x_convocatoria = self._crear_proyecto_x_convocatoria()
        self.fase_1 = self._crear_tipo_calificacion(nombre='Fase 1', orden=1)
        self.fase_2 = self._crear_tipo_calificacion(nombre='Fase 2', orden=2)

    def test_crear_calificacion_exitoso(self):
        calificacion = CalificacionService.crear(
            fase_id=self.fase_1.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        self.assertFalse(calificacion.aprobado)
        self.assertTrue(calificacion.primer_sin_observacion)

    def test_crear_calificacion_duplicada_falla(self):
        CalificacionService.crear(
            fase_id=self.fase_1.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            CalificacionService.crear(
                fase_id=self.fase_1.pk,
                aplicar_id=self.proyecto_x_convocatoria.pk,
                ejecutor=self.ejecutor,
            )

    def test_crear_calificacion_sin_fase_falla(self):
        with self.assertRaises(ValidationError):
            CalificacionService.crear(
                fase_id=None,
                aplicar_id=self.proyecto_x_convocatoria.pk,
                ejecutor=self.ejecutor,
            )

    def test_calificar_fase_aprobada_habilita_siguiente_fase(self):
        calificacion_1 = CalificacionService.crear(
            fase_id=self.fase_1.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        calificacion_2 = CalificacionService.crear(
            fase_id=self.fase_2.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        calificacion_2.primer_sin_observacion = False
        calificacion_2.save(update_fields=['primer_sin_observacion'])

        CalificacionService.calificar_fase(
            calificacion_id=calificacion_1.pk,
            aprobado=True,
            observacion='Todo en orden',
            ejecutor=self.ejecutor,
        )

        calificacion_2.refresh_from_db()
        self.assertTrue(calificacion_2.primer_sin_observacion)

    def test_calificar_fase_no_aprobada_finaliza_proyecto_x_convocatoria(self):
        calificacion_1 = CalificacionService.crear(
            fase_id=self.fase_1.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        CalificacionService.calificar_fase(
            calificacion_id=calificacion_1.pk,
            aprobado=False,
            observacion='No cumple los requisitos',
            ejecutor=self.ejecutor,
        )

        self.proyecto_x_convocatoria.refresh_from_db()
        self.assertTrue(self.proyecto_x_convocatoria.estado_finalizado_calificacion)
        self.assertEqual(
            self.proyecto_x_convocatoria.calificacion_ultimo_filtro_calificacion, 'NO_APROBADO'
        )
        self.proyecto_x_convocatoria.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto_x_convocatoria.proyecto.estado_aprobado, 'NO_APROBADO')

    def test_calificar_fase_no_aprobada_sin_observacion_falla(self):
        calificacion_1 = CalificacionService.crear(
            fase_id=self.fase_1.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            CalificacionService.calificar_fase(
                calificacion_id=calificacion_1.pk,
                aprobado=False,
                observacion='',
                ejecutor=self.ejecutor,
            )

    def test_calificar_todas_las_fases_aprobadas_finaliza_proyecto_como_aprobado(self):
        calificacion_1 = CalificacionService.crear(
            fase_id=self.fase_1.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        calificacion_2 = CalificacionService.crear(
            fase_id=self.fase_2.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )

        CalificacionService.calificar_fase(
            calificacion_id=calificacion_1.pk, aprobado=True,
            observacion='OK', ejecutor=self.ejecutor,
        )
        CalificacionService.calificar_fase(
            calificacion_id=calificacion_2.pk, aprobado=True,
            observacion='OK', ejecutor=self.ejecutor,
        )

        self.proyecto_x_convocatoria.refresh_from_db()
        self.assertTrue(self.proyecto_x_convocatoria.estado_finalizado_calificacion)
        self.proyecto_x_convocatoria.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto_x_convocatoria.proyecto.estado_aprobado, 'APROBADO')

    def test_listar_por_proyecto_x_convocatoria(self):
        CalificacionService.crear(
            fase_id=self.fase_1.pk,
            aplicar_id=self.proyecto_x_convocatoria.pk,
            ejecutor=self.ejecutor,
        )
        resultado = CalificacionService.listar_por_proyecto_x_convocatoria(
            self.proyecto_x_convocatoria.pk
        )
        self.assertEqual(resultado.count(), 1)