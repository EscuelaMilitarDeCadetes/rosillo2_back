from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.tipo_calificacion_service import TipoCalificacionService


class TipoCalificacionServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def test_crear_tipo_calificacion_exitoso(self):
        fase = TipoCalificacionService.crear(
            tipo_calificacion='Fase Documental',
            descripcion='Revisión de documentos',
            evaluacion=False,
            orden_fase=1,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(fase.orden_fase, 1)

    def test_crear_tipo_calificacion_nombre_duplicado_falla(self):
        TipoCalificacionService.crear(
            tipo_calificacion='Fase Única', descripcion='Desc', evaluacion=False,
            orden_fase=1, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            TipoCalificacionService.crear(
                tipo_calificacion='fase única', descripcion='Otra desc', evaluacion=True,
                orden_fase=2, ejecutor=self.ejecutor,
            )

    def test_crear_tipo_calificacion_orden_duplicado_falla(self):
        TipoCalificacionService.crear(
            tipo_calificacion='Fase A', descripcion='Desc A', evaluacion=False,
            orden_fase=1, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            TipoCalificacionService.crear(
                tipo_calificacion='Fase B', descripcion='Desc B', evaluacion=False,
                orden_fase=1, ejecutor=self.ejecutor,
            )

    def test_crear_tipo_calificacion_orden_invalido_falla(self):
        with self.assertRaises(ValidationError):
            TipoCalificacionService.crear(
                tipo_calificacion='Fase Inválida', descripcion='Desc', evaluacion=False,
                orden_fase=0, ejecutor=self.ejecutor,
            )

    def test_actualizar_tipo_calificacion_exitoso(self):
        fase = TipoCalificacionService.crear(
            tipo_calificacion='Fase Original', descripcion='Desc', evaluacion=False,
            orden_fase=1, ejecutor=self.ejecutor,
        )
        actualizada = TipoCalificacionService.actualizar(
            tipo_calificacion_id=fase.pk,
            tipo_calificacion='Fase Corregida',
            descripcion='Desc corregida',
            evaluacion=True,
            orden_fase=1,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.tipo_calificacion, 'Fase Corregida')
        self.assertTrue(actualizada.evaluacion)

    def test_listar_evaluables(self):
        TipoCalificacionService.crear(
            tipo_calificacion='Fase Evaluable', descripcion='Desc', evaluacion=True,
            orden_fase=1, ejecutor=self.ejecutor,
        )
        TipoCalificacionService.crear(
            tipo_calificacion='Fase No Evaluable', descripcion='Desc', evaluacion=False,
            orden_fase=2, ejecutor=self.ejecutor,
        )
        resultado = TipoCalificacionService.listar_evaluables()
        self.assertEqual(resultado.count(), 1)