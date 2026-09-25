from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.modalidad_x_facultad_service import (
    ModalidadXFacultadService,
)


class ModalidadXFacultadServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.otra_facultad = self._crear_facultad(nombre='Facultad de Derecho', abreviatura='DER')

    def _crear_vinculo(self):
        return ModalidadXFacultadService.crear(
            facultad_id=self.otra_facultad.pk,
            modalidad_id=self.modalidad.pk,
            ejecutor=self.ejecutor,
        )

    def test_crear_vinculo_exitoso(self):
        vinculo = self._crear_vinculo()
        self.assertTrue(vinculo.disponible)

    def test_crear_vinculo_duplicado_falla(self):
        self._crear_vinculo()
        with self.assertRaises(ValidationError):
            self._crear_vinculo()

    def test_deshabilitar_y_habilitar_vinculo(self):
        vinculo = self._crear_vinculo()
        ModalidadXFacultadService.deshabilitar(vinculo.pk, ejecutor=self.ejecutor)
        vinculo.refresh_from_db()
        self.assertFalse(vinculo.disponible)

        habilitado = ModalidadXFacultadService.habilitar(vinculo.pk, ejecutor=self.ejecutor)
        self.assertTrue(habilitado.disponible)

    def test_habilitar_vinculo_ya_disponible_falla(self):
        vinculo = self._crear_vinculo()
        with self.assertRaises(ValidationError):
            ModalidadXFacultadService.habilitar(vinculo.pk, ejecutor=self.ejecutor)    

    def test_listar_por_facultad(self):
        self._crear_vinculo()
        resultado = ModalidadXFacultadService.listar_por_facultad(self.otra_facultad.pk)
        self.assertEqual(resultado.count(), 1)