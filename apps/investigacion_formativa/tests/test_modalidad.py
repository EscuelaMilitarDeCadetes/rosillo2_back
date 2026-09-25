from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.modalidad_service import ModalidadService


class ModalidadServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_modalidad(self, nombre='Práctica Social', codigo='PS'):
        return ModalidadService.crear(
            nombre=nombre, codigo=codigo, ejecutor=self.ejecutor,
            requiere_tutor=True, requiere_antiplagio=True, requiere_sustentacion=False,
        )

    def test_crear_modalidad_exitosa(self):
        modalidad = self._crear_modalidad()
        self.assertTrue(modalidad.activo)
        self.assertTrue(modalidad.requiere_tutor)

    def test_crear_modalidad_nombre_duplicado_falla(self):
        self._crear_modalidad(nombre='Práctica Social', codigo='PS1')
        with self.assertRaises(ValidationError):
            self._crear_modalidad(nombre='Práctica Social', codigo='PS2')

    def test_crear_modalidad_sin_nombre_falla(self):
        with self.assertRaises(ValidationError):
            ModalidadService.crear(nombre='', codigo='PS', ejecutor=self.ejecutor)

    def test_actualizar_modalidad_exitoso(self):
        modalidad = self._crear_modalidad()
        actualizada = ModalidadService.actualizar(
            modalidad_id=modalidad.pk,
            nombre='Práctica Social Comunitaria',
            codigo='PS',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.nombre, 'Práctica Social Comunitaria')

    def test_desactivar_y_activar_modalidad(self):
        modalidad = self._crear_modalidad()
        ModalidadService.eliminar(modalidad.pk, ejecutor=self.ejecutor)
        modalidad.refresh_from_db()
        self.assertFalse(modalidad.activo)

        activada = ModalidadService.activar(modalidad.pk, ejecutor=self.ejecutor)
        self.assertTrue(activada.activo)

    def test_activar_modalidad_ya_activa_falla(self):
        modalidad = self._crear_modalidad()
        with self.assertRaises(ValidationError):
            ModalidadService.activar(modalidad.pk, ejecutor=self.ejecutor)

    def test_eliminar_modalidad_ya_desactivada_falla(self):
        modalidad = self._crear_modalidad()
        ModalidadService.eliminar(modalidad.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            ModalidadService.eliminar(modalidad.pk, ejecutor=self.ejecutor)

    def test_listar_activas_excluye_desactivadas(self):
        modalidad = self._crear_modalidad()
        ModalidadService.eliminar(modalidad.pk, ejecutor=self.ejecutor)
        # self.modalidad (de la fixture base) sigue activa
        resultado = ModalidadService.listar_activas()
        self.assertNotIn(modalidad.pk, [m.pk for m in resultado])
        self.assertIn(self.modalidad.pk, [m.pk for m in resultado])