# apps/investigacion_formativa/tests/test_estudiante.py

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.estudiante_service import EstudianteService


class EstudianteServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def test_crear_estudiante_exitoso(self):
        estudiante = EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        self.assertTrue(estudiante.estado)

    def test_crear_estudiante_correo_invalido_falla(self):
        with self.assertRaises(ValidationError):
            EstudianteService.crear(
                persona_id=self.persona.pk,
                modalidad_facultad_id=self.modalidad_facultad.pk,
                correo_personal='no-es-un-correo',
                nivel='Décimo semestre',
                ejecutor=self.ejecutor,
            )

    def test_crear_estudiante_duplicado_en_misma_modalidad_facultad_falla(self):
        EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EstudianteService.crear(
                persona_id=self.persona.pk,
                modalidad_facultad_id=self.modalidad_facultad.pk,
                correo_personal='otro.correo@gmail.com',
                nivel='Noveno semestre',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_estudiante_exitoso(self):
        estudiante = EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        actualizado = EstudianteService.actualizar(
            estudiante_id=estudiante.pk,
            correo_personal='nuevo.correo@gmail.com',
            nivel='Undécimo semestre',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.correo_personal, 'nuevo.correo@gmail.com')

    def test_eliminar_estudiante_activo_exitoso(self):
        estudiante = EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        eliminado = EstudianteService.eliminar(estudiante.pk, ejecutor=self.ejecutor)
        self.assertFalse(eliminado.estado)

    def test_eliminar_estudiante_ya_desactivado_falla(self):
        estudiante = EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        EstudianteService.eliminar(estudiante.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            EstudianteService.eliminar(estudiante.pk, ejecutor=self.ejecutor)

    def test_activar_estudiante_desactivado_exitoso(self):
        estudiante = EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        EstudianteService.eliminar(estudiante.pk, ejecutor=self.ejecutor)
        reactivado = EstudianteService.activar(estudiante.pk, ejecutor=self.ejecutor)
        self.assertTrue(reactivado.estado)

    def test_activar_estudiante_ya_activo_falla(self):
        estudiante = EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EstudianteService.activar(estudiante.pk, ejecutor=self.ejecutor)

    def test_listar_por_modalidad_facultad(self):
        EstudianteService.crear(
            persona_id=self.persona.pk,
            modalidad_facultad_id=self.modalidad_facultad.pk,
            correo_personal='ana.gomez@gmail.com',
            nivel='Décimo semestre',
            ejecutor=self.ejecutor,
        )
        resultado = EstudianteService.listar_por_modalidad_facultad(self.modalidad_facultad.pk)
        self.assertEqual(resultado.count(), 1)