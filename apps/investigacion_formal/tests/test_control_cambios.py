from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.control_cambios_service import ControlCambiosService


class ControlCambiosServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proyecto = self._crear_proyecto()

    def test_crear_control_cambios_exitoso(self):
        control = ControlCambiosService.crear(
            proyecto_id=self.proyecto.pk,
            tipo_cambio='Cambio de fechas',
            ejecutor=self.ejecutor,
            cambio_tiempo=True,
        )
        self.assertTrue(control.cambio_tiempo)
        self.assertFalse(control.cambio_costo)

    def test_crear_control_cambios_sin_ninguna_bandera_falla(self):
        with self.assertRaises(ValidationError):
            ControlCambiosService.crear(
                proyecto_id=self.proyecto.pk,
                tipo_cambio='Cambio sin marcar nada',
                ejecutor=self.ejecutor,
            )

    def test_crear_control_cambios_sin_tipo_cambio_falla(self):
        with self.assertRaises(ValidationError):
            ControlCambiosService.crear(
                proyecto_id=self.proyecto.pk,
                tipo_cambio='',
                ejecutor=self.ejecutor,
                cambio_costo=True,
            )

    def test_actualizar_banderas_exitoso(self):
        control = ControlCambiosService.crear(
            proyecto_id=self.proyecto.pk,
            tipo_cambio='Cambio de investigador',
            ejecutor=self.ejecutor,
            cambio_investigador=True,
        )
        actualizado = ControlCambiosService.actualizar_banderas(
            control_cambios_id=control.pk,
            ejecutor=self.ejecutor,
            cambio_investigador=False,
            cambio_producto=True,
        )
        self.assertFalse(actualizado.cambio_investigador)
        self.assertTrue(actualizado.cambio_producto)

    def test_actualizar_banderas_dejando_todas_en_false_falla(self):
        control = ControlCambiosService.crear(
            proyecto_id=self.proyecto.pk,
            tipo_cambio='Cambio de costo',
            ejecutor=self.ejecutor,
            cambio_costo=True,
        )
        with self.assertRaises(ValidationError):
            ControlCambiosService.actualizar_banderas(
                control_cambios_id=control.pk,
                ejecutor=self.ejecutor,
                cambio_costo=False,
            )

    def test_tipo_cambio_y_proyecto_no_se_modifican_en_actualizar_banderas(self):
        """El registro es append-only salvo por las 4 banderas booleanas."""
        control = ControlCambiosService.crear(
            proyecto_id=self.proyecto.pk,
            tipo_cambio='Cambio original',
            ejecutor=self.ejecutor,
            cambio_producto=True,
        )
        actualizado = ControlCambiosService.actualizar_banderas(
            control_cambios_id=control.pk,
            ejecutor=self.ejecutor,
            cambio_producto=True,
            cambio_costo=True,
        )
        self.assertEqual(actualizado.tipo_cambio, 'Cambio original')
        self.assertEqual(actualizado.proyecto_id, self.proyecto.pk)

    def test_listar_por_proyecto(self):
        ControlCambiosService.crear(
            proyecto_id=self.proyecto.pk,
            tipo_cambio='Cambio 1',
            ejecutor=self.ejecutor,
            cambio_tiempo=True,
        )
        otro_proyecto = self._crear_proyecto(titulo='Otro proyecto')
        ControlCambiosService.crear(
            proyecto_id=otro_proyecto.pk,
            tipo_cambio='Cambio 2',
            ejecutor=self.ejecutor,
            cambio_costo=True,
        )
        resultado = ControlCambiosService.listar_por_proyecto(self.proyecto.pk)
        self.assertEqual(resultado.count(), 1)