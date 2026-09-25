# apps/investigacion_formativa/tests/test_homologacion.py
from datetime import date

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.models import Modalidad, FlujoProceso
from apps.investigacion_formativa.services.homologacion_service import HomologacionService


class HomologacionServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.modalidad_homologable = Modalidad.objects.create(
            nombre='Modalidad Homologable de Prueba',
            codigo='MHP',
            activo=True,
            requiere_evaluadores=True,
            permite_homologacion=True,
        )
        self.flujo_homologable = FlujoProceso.objects.create(
            modalidad=self.modalidad_homologable,
            nombre='Flujo Homologable v1',
            version=1,
            tipo='FORMATIVA',
            activo=True,
            fecha_vigencia_inicio=date(2024, 1, 1),
        )
        self.proceso_homologable = self._crear_proceso_formativo(
            titulo='Proceso Homologable de Prueba',
            flujo_version=self.flujo_homologable,
        )

    def _crear_homologacion(self):
        return HomologacionService.crear(
            proceso_id=self.proceso_homologable.pk,
            ejecutor=self.ejecutor,
            observaciones='Solicitud de homologación de certificado externo.',
        )

    def test_crear_homologacion_exitosa(self):
        homologacion = self._crear_homologacion()
        self.assertEqual(homologacion.estado, 'PENDIENTE')

    def test_crear_homologacion_para_modalidad_no_homologable_falla(self):
        # self.proceso (fixture base) usa self.modalidad, con
        # permite_homologacion=False.
        with self.assertRaises(ValidationError):
            HomologacionService.crear(
                proceso_id=self.proceso.pk,
                ejecutor=self.ejecutor,
                observaciones='No debería poder crearse.',
            )

    def test_crear_homologacion_duplicada_para_proceso_falla(self):
        self._crear_homologacion()
        with self.assertRaises(ValidationError):
            self._crear_homologacion()

    def test_aprobar_homologacion_exitoso(self):
        homologacion = self._crear_homologacion()
        aprobada = HomologacionService.aprobar(
            homologacion_id=homologacion.pk,
            aprobado_por_id=self.ejecutor.pk,
            creditos_reconocidos=6,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(aprobada.estado, 'APROBADA')
        self.assertEqual(aprobada.creditos_reconocidos, 6)
        self.assertIsNotNone(aprobada.fecha_homologacion)

    def test_aprobar_homologacion_dos_veces_falla(self):
        homologacion = self._crear_homologacion()
        HomologacionService.aprobar(
            homologacion_id=homologacion.pk, aprobado_por_id=self.ejecutor.pk,
            creditos_reconocidos=6, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            HomologacionService.aprobar(
                homologacion_id=homologacion.pk, aprobado_por_id=self.ejecutor.pk,
                creditos_reconocidos=6, ejecutor=self.ejecutor,
            )

    def test_rechazar_homologacion_exitoso(self):
        homologacion = self._crear_homologacion()
        rechazada = HomologacionService.rechazar(
            homologacion_id=homologacion.pk,
            observaciones='El certificado no corresponde a la línea de investigación.',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(rechazada.estado, 'RECHAZADA')

    def test_rechazar_homologacion_sin_observaciones_falla(self):
        homologacion = self._crear_homologacion()
        with self.assertRaises(ValidationError):
            HomologacionService.rechazar(
                homologacion_id=homologacion.pk, observaciones='', ejecutor=self.ejecutor,
            )

    def test_obtener_por_proceso(self):
        homologacion = self._crear_homologacion()
        encontrada = HomologacionService.obtener_por_proceso(self.proceso_homologable.pk)
        self.assertEqual(encontrada.pk, homologacion.pk)