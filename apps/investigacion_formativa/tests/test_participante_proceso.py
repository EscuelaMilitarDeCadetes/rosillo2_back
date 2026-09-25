from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.participante_proceso_service import (
    ParticipanteProcesoService,
)


class ParticipanteProcesoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.otra_persona = self._crear_persona(nombre='Marta', apellido='López', documento='321654987')

    def _crear_participante(self, proceso=None, rol_en_modalidad='JURADO'):
        return ParticipanteProcesoService.crear(
            proceso_formativo_id=self.proceso.pk,
            persona_id=self.otra_persona.pk,
            rol_en_modalidad=rol_en_modalidad,
            ejecutor=self.ejecutor,
        )

    def test_crear_participante_exitoso(self):
        participante = self._crear_participante()
        self.assertTrue(participante.activo)
        self.assertIsNone(participante.fecha_finalizacion)

    def test_crear_participante_duplicado_para_mismo_proceso_falla(self):
        self._crear_participante()
        with self.assertRaises(ValidationError):
            self._crear_participante(rol_en_modalidad='ESTUDIANTE')

    def test_crear_participante_rol_invalido_falla(self):
        with self.assertRaises(ValidationError):
            self._crear_participante(rol_en_modalidad='DIRECTOR')

    def test_actualizar_participante_exitoso(self):
        participante = self._crear_participante(rol_en_modalidad='JURADO')
        actualizado = ParticipanteProcesoService.actualizar(
            participante_id=participante.pk,
            rol_en_modalidad='COORDINADOR',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.rol_en_modalidad, 'COORDINADOR')

    def test_finalizar_participante_exitoso(self):
        participante = self._crear_participante()
        finalizado = ParticipanteProcesoService.finalizar(participante.pk, ejecutor=self.ejecutor)
        self.assertFalse(finalizado.activo)
        self.assertIsNotNone(finalizado.fecha_finalizacion)
        self.assertEqual(finalizado.fecha_finalizacion, timezone.now().date())

    def test_finalizar_participante_dos_veces_falla(self):
        participante = self._crear_participante()
        ParticipanteProcesoService.finalizar(participante.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            ParticipanteProcesoService.finalizar(participante.pk, ejecutor=self.ejecutor)

    def test_eliminar_participante_soft_delete(self):
        participante = self._crear_participante()
        ParticipanteProcesoService.eliminar(participante.pk, ejecutor=self.ejecutor)
        participante.refresh_from_db()
        self.assertFalse(participante.activo)

    def test_listar_por_proceso_incluye_al_ya_creado_en_la_fixture(self):
        self._crear_participante()
        resultado = ParticipanteProcesoService.listar_por_proceso(self.proceso.pk)
        # self.participante (de la fixture base) + el nuevo creado en este test
        self.assertEqual(resultado.count(), 3)