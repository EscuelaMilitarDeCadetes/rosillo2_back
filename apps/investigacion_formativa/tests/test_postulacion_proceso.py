from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.models import Estudiante
from apps.investigacion_formativa.services.postulacion_proceso_service import (
    PostulacionProcesoService,
)


class PostulacionProcesoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.estudiante = Estudiante.objects.create(
            persona=self.persona,
            modalidad_facultad=self.modalidad_x_facultad,
            correo_personal='ana.personal@gmail.com',
            nivel='PREGRADO',
            estado=True,
        )

    def _crear_postulacion(self, promedio_actual=4.2):
        return PostulacionProcesoService.crear(
            estudiante_id=self.estudiante.pk,
            modalidad_id=self.modalidad_x_facultad.pk,
            promedio_actual=promedio_actual,
            ejecutor=self.ejecutor,
        )

    def test_crear_postulacion_exitosa(self):
        postulacion = self._crear_postulacion()
        self.assertEqual(postulacion.estado, 'BORRADOR')
        self.assertEqual(postulacion.promedio_actual, 4.2)

    def test_crear_postulacion_duplicada_falla(self):
        self._crear_postulacion()
        with self.assertRaises(ValidationError):
            self._crear_postulacion()

    def test_crear_postulacion_promedio_fuera_de_rango_falla(self):
        with self.assertRaises(ValidationError):
            self._crear_postulacion(promedio_actual=6.0)

    def test_actualizar_postulacion_en_borrador_exitoso(self):
        postulacion = self._crear_postulacion()
        actualizada = PostulacionProcesoService.actualizar(
            postulacion_id=postulacion.pk, promedio_actual=4.5, ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.promedio_actual, 4.5)

    def test_actualizar_postulacion_enviada_falla(self):
        postulacion = self._crear_postulacion()
        PostulacionProcesoService.enviar(postulacion.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            PostulacionProcesoService.actualizar(
                postulacion_id=postulacion.pk, promedio_actual=4.5, ejecutor=self.ejecutor,
            )

    def test_flujo_completo_enviar_validar_aprobar(self):
        postulacion = self._crear_postulacion()
        PostulacionProcesoService.enviar(postulacion.pk, ejecutor=self.ejecutor)
        PostulacionProcesoService.pasar_a_validacion(postulacion.pk, ejecutor=self.ejecutor)
        aprobada = PostulacionProcesoService.aprobar(
            postulacion_id=postulacion.pk,
            flujo_version_id=self.flujo.pk,
            titulo='Proceso generado desde postulación',
            observacion='Observación del proceso generado',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-06-30',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(aprobada.estado, 'APROBADA')
        self.assertIsNotNone(aprobada.proceso_creado)
        self.assertEqual(aprobada.proceso_creado.titulo, 'Proceso generado desde postulación')

    def test_aprobar_sin_pasar_por_validacion_falla(self):
        postulacion = self._crear_postulacion()
        PostulacionProcesoService.enviar(postulacion.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            PostulacionProcesoService.aprobar(
                postulacion_id=postulacion.pk,
                flujo_version_id=self.flujo.pk,
                titulo='Proceso generado',
                observacion='Observación',
                fecha_inicio='2025-01-01',
                fecha_fin='2025-06-30',
                ejecutor=self.ejecutor,
            )

    def test_rechazar_postulacion_exitoso(self):
        postulacion = self._crear_postulacion()
        PostulacionProcesoService.enviar(postulacion.pk, ejecutor=self.ejecutor)
        rechazada = PostulacionProcesoService.rechazar(
            postulacion_id=postulacion.pk,
            observacion_coordinacion='El promedio no cumple el mínimo institucional.',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(rechazada.estado, 'RECHAZADA')

    def test_rechazar_sin_observacion_falla(self):
        postulacion = self._crear_postulacion()
        PostulacionProcesoService.enviar(postulacion.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            PostulacionProcesoService.rechazar(
                postulacion_id=postulacion.pk, observacion_coordinacion='', ejecutor=self.ejecutor,
            )

    def test_eliminar_postulacion_en_borrador_exitoso(self):
        postulacion = self._crear_postulacion()
        pk = postulacion.pk
        eliminada = PostulacionProcesoService.eliminar(pk, ejecutor=self.ejecutor)
        self.assertEqual(eliminada.estado, 'ELIMINADA')
        self.assertTrue(PostulacionProcesoService.listar().filter(pk=pk).exists())

    def test_eliminar_postulacion_enviada_falla(self):
        postulacion = self._crear_postulacion()
        PostulacionProcesoService.enviar(postulacion.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            PostulacionProcesoService.eliminar(postulacion.pk, ejecutor=self.ejecutor)