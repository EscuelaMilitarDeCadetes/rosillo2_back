from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.evento_evaluativo_service import (
    EventoEvaluativoService,
)


class EventoEvaluativoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def _crear_evento(self, numero=1, fecha_sustentacion='2025-07-01T10:00:00Z'):
        return EventoEvaluativoService.crear(
            proceso_formativo_id=self.proceso.pk,
            numero=numero,
            es_obligatoria=True,
            fecha_sustentacion=fecha_sustentacion,
            lugar='Auditorio Principal',
            ejecutor=self.ejecutor,
        )

    def test_crear_evento_exitoso(self):
        evento = self._crear_evento()
        self.assertEqual(evento.resultado, 'PENDIENTE')
        self.assertTrue(evento.es_obligatoria)

    def test_crear_evento_sin_lugar_falla(self):
        with self.assertRaises(ValidationError):
            EventoEvaluativoService.crear(
                proceso_formativo_id=self.proceso.pk,
                numero=1,
                es_obligatoria=True,
                fecha_sustentacion='2025-07-01T10:00:00Z',
                lugar='',
                ejecutor=self.ejecutor,
            )

    def test_reprogramar_evento_exitoso(self):
        evento = self._crear_evento()
        reprogramado = EventoEvaluativoService.reprogramar(
            evento_id=evento.pk,
            fecha_sustentacion='2025-07-10T14:00:00Z',
            lugar='Sala de Grados',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(reprogramado.lugar, 'Sala de Grados')

    def test_registrar_resultado_exitoso(self):
        evento = self._crear_evento()
        con_resultado = EventoEvaluativoService.registrar_resultado(
            evento_id=evento.pk, resultado='APROBADO', ejecutor=self.ejecutor,
        )
        self.assertEqual(con_resultado.resultado, 'APROBADO')

    def test_registrar_resultado_dos_veces_falla(self):
        evento = self._crear_evento()
        EventoEvaluativoService.registrar_resultado(
            evento_id=evento.pk, resultado='APROBADO', ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EventoEvaluativoService.registrar_resultado(
                evento_id=evento.pk, resultado='REPROBADO', ejecutor=self.ejecutor,
            )

    def test_eliminar_evento_pendiente_hard_delete(self):
        evento = self._crear_evento()
        pk = evento.pk
        EventoEvaluativoService.eliminar(pk, ejecutor=self.ejecutor)
        self.assertFalse(EventoEvaluativoService.listar().filter(pk=pk).exists())

    def test_eliminar_evento_con_resultado_registrado_falla(self):
        evento = self._crear_evento()
        EventoEvaluativoService.registrar_resultado(
            evento_id=evento.pk, resultado='APROBADO', ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EventoEvaluativoService.eliminar(evento.pk, ejecutor=self.ejecutor)

    def test_listar_por_proceso(self):
        self._crear_evento(numero=1)
        resultado = EventoEvaluativoService.listar_por_proceso(self.proceso.pk)
        self.assertEqual(resultado.count(), 1)