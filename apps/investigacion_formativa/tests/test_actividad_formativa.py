# apps/investigacion_formativa/tests/test_actividad_formativa.py
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.actividad_formativa_service import ActividadFormativaService


class ActividadFormativaServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proceso = self._crear_proceso_formativo()

    def test_crear_actividad_exitosa(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Seguimiento mensual',
            ejecutor=self.ejecutor,
            descripcion='Reporte de avance',
            fecha_inicio='2024-02-01',
            fecha_fin='2024-02-15',
            horas_dedicadas=10,
        )
        self.assertEqual(actividad.estado, 'PLANIFICADA')
        self.assertEqual(actividad.nombre, 'Seguimiento mensual')

    def test_crear_actividad_nombre_vacio_falla(self):
        with self.assertRaises(ValidationError):
            ActividadFormativaService.crear(
                proceso_formativo_id=self.proceso.pk,
                responsable_id=self.persona.pk,
                nombre='',
                ejecutor=self.ejecutor,
            )

    def test_crear_actividad_fecha_fin_anterior_a_inicio_falla(self):
        with self.assertRaises(ValidationError):
            ActividadFormativaService.crear(
                proceso_formativo_id=self.proceso.pk,
                responsable_id=self.persona.pk,
                nombre='Actividad inválida',
                ejecutor=self.ejecutor,
                fecha_inicio='2024-02-15',
                fecha_fin='2024-02-01',
            )

    def test_crear_actividad_horas_negativas_falla(self):
        with self.assertRaises(ValidationError):
            ActividadFormativaService.crear(
                proceso_formativo_id=self.proceso.pk,
                responsable_id=self.persona.pk,
                nombre='Actividad inválida',
                ejecutor=self.ejecutor,
                horas_dedicadas=-5,
            )

    def test_actualizar_actividad_exitosa(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad original',
            descripcion='Descripción original',
            ejecutor=self.ejecutor,
        )
        actualizada = ActividadFormativaService.actualizar(
            actividad_id=actividad.pk,
            nombre='Actividad renombrada',
            ejecutor=self.ejecutor,
            descripcion='Nueva descripción',
        )
        self.assertEqual(actualizada.nombre, 'Actividad renombrada')

    def test_actualizar_actividad_completada_falla(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad a completar',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)
        documento = self._crear_documento_firma('Soporte actividad 1')
        ActividadFormativaService.completar(
            actividad.pk, ejecutor=self.ejecutor, documento_soporte_id=documento.pk
        )
        with self.assertRaises(ValidationError):
            ActividadFormativaService.actualizar(
                actividad_id=actividad.pk,
                nombre='Intento de edición',
                ejecutor=self.ejecutor,
            )

    def test_iniciar_actividad_exitoso(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad a iniciar',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        iniciada = ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)
        self.assertEqual(iniciada.estado, 'EN_PROGRESO')

    def test_iniciar_actividad_no_planificada_falla(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad ya iniciada',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)

    def test_completar_actividad_exitoso(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad a completar',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)
        documento = self._crear_documento_firma('Soporte actividad 2')
        completada = ActividadFormativaService.completar(
            actividad.pk, ejecutor=self.ejecutor, documento_soporte_id=documento.pk
        )
        self.assertEqual(completada.estado, 'COMPLETADA')
        self.assertEqual(completada.documento_soporte_id, documento.pk)

    def test_completar_actividad_sin_documento_soporte_falla(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad sin soporte',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            ActividadFormativaService.completar(actividad.pk, ejecutor=self.ejecutor)

    def test_completar_actividad_no_en_progreso_falla(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad planificada',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        documento = self._crear_documento_firma('Soporte actividad 3')
        with self.assertRaises(ValidationError):
            ActividadFormativaService.completar(
                actividad.pk, ejecutor=self.ejecutor, documento_soporte_id=documento.pk
            )

    def test_cancelar_actividad_exitoso(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad a cancelar',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        cancelada = ActividadFormativaService.cancelar(actividad.pk, ejecutor=self.ejecutor)
        self.assertEqual(cancelada.estado, 'CANCELADA')

    def test_cancelar_actividad_completada_falla(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad a completar antes de cancelar',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)
        documento = self._crear_documento_firma('Soporte actividad 4')
        ActividadFormativaService.completar(
            actividad.pk, ejecutor=self.ejecutor, documento_soporte_id=documento.pk
        )
        with self.assertRaises(ValidationError):
            ActividadFormativaService.cancelar(actividad.pk, ejecutor=self.ejecutor)

    def test_eliminar_actividad_planificada_exitoso(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad a eliminar',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        resultado = ActividadFormativaService.eliminar(actividad.pk, ejecutor=self.ejecutor)
        self.assertTrue(resultado)
        self.assertFalse(ActividadFormativaService.listar().filter(pk=actividad.pk).exists())

    def test_eliminar_actividad_iniciada_falla(self):
        actividad = ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad no eliminable',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        ActividadFormativaService.iniciar(actividad.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            ActividadFormativaService.eliminar(actividad.pk, ejecutor=self.ejecutor)

    def test_listar_por_proceso(self):
        ActividadFormativaService.crear(
            proceso_formativo_id=self.proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad del proceso',
            descripcion='Descripción de la actividad',
            ejecutor=self.ejecutor,
        )
        otro_proceso = self._crear_proceso_formativo(titulo='Otro proceso')
        ActividadFormativaService.crear(
            proceso_formativo_id=otro_proceso.pk,
            responsable_id=self.persona.pk,
            nombre='Actividad de otro proceso',
            ejecutor=self.ejecutor,
        )
        actividades = ActividadFormativaService.listar_por_proceso(self.proceso.pk)
        self.assertEqual(actividades.count(), 1)