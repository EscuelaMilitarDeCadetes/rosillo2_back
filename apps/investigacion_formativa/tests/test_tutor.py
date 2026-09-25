from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.tutor_service import TutorService


class TutorServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def test_crear_tutor_exitoso(self):
        tutor = TutorService.crear(
            persona_id=self.persona.pk, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
        )
        self.assertTrue(tutor.estado)

    def test_crear_tutor_persona_duplicada_falla(self):
        TutorService.crear(
            persona_id=self.persona.pk, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
        )
        otra_facultad = self._crear_facultad()
        with self.assertRaises(ValidationError):
            TutorService.crear(
                persona_id=self.persona.pk, facultad_id=otra_facultad.pk, ejecutor=self.ejecutor,
            )

    def test_crear_tutor_sin_persona_falla(self):
        with self.assertRaises(ValidationError):
            TutorService.crear(
                persona_id=None, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
            )

    def test_actualizar_tutor_exitoso(self):
        tutor = TutorService.crear(
            persona_id=self.persona.pk, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
        )
        otra_facultad = self._crear_facultad()
        actualizado = TutorService.actualizar(
            tutor_id=tutor.pk, facultad_id=otra_facultad.pk, ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.facultad_id, otra_facultad.pk)

    def test_desactivar_tutor_exitoso(self):
        tutor = TutorService.crear(
            persona_id=self.persona.pk, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
        )
        desactivado = TutorService.desactivar(tutor.pk, ejecutor=self.ejecutor)
        self.assertFalse(desactivado.estado)

    def test_desactivar_tutor_ya_inactivo_falla(self):
        tutor = TutorService.crear(
            persona_id=self.persona.pk, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
        )
        TutorService.desactivar(tutor.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            TutorService.desactivar(tutor.pk, ejecutor=self.ejecutor)

    def test_activar_tutor_exitoso(self):
        tutor = TutorService.crear(
            persona_id=self.persona.pk, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
        )
        TutorService.desactivar(tutor.pk, ejecutor=self.ejecutor)
        activado = TutorService.activar(tutor.pk, ejecutor=self.ejecutor)
        self.assertTrue(activado.estado)

    def test_listar_activos_por_facultad(self):
        tutor = TutorService.crear(
            persona_id=self.persona.pk, facultad_id=self.facultad.pk, ejecutor=self.ejecutor,
        )
        TutorService.desactivar(tutor.pk, ejecutor=self.ejecutor)
        resultado = TutorService.listar_activos_por_facultad(self.facultad.pk)
        self.assertEqual(resultado.count(), 0)