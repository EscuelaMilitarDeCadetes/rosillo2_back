# apps/investigacion_formativa/tests/test_certificacion_externa.py

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.certificacion_externa_service import (
    CertificacionExternaService,
)


class CertificacionExternaServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proceso = self._crear_proceso_formativo()

    def _crear_certificacion(self, **kwargs):
        datos = dict(
            proceso_id=self.proceso.pk,
            tipo='DIPLOMADO',
            nombre_programa='Diplomado en IA',
            institucion='Universidad de Prueba',
            horas_certificadas=100,
            fecha_inicio='2024-01-01',
            fecha_fin='2024-03-01',
            ejecutor=self.ejecutor,
        )
        datos.update(kwargs)
        return CertificacionExternaService.crear(**datos)

    def test_crear_certificacion_exitosa(self):
        certificacion = self._crear_certificacion()
        self.assertEqual(certificacion.horas_validadas, 0)
        self.assertFalse(certificacion.cumple_horas)

    def test_crear_certificacion_tipo_invalido_falla(self):
        with self.assertRaises(ValidationError):
            self._crear_certificacion(tipo='NO_EXISTE')

    def test_crear_certificacion_horas_certificadas_invalidas_falla(self):
        with self.assertRaises(ValidationError):
            self._crear_certificacion(horas_certificadas=0)

    def test_crear_certificacion_fecha_fin_anterior_a_inicio_falla(self):
        with self.assertRaises(ValidationError):
            self._crear_certificacion(fecha_inicio='2024-03-01', fecha_fin='2024-01-01')
            
    def test_actualizar_certificacion_pendiente_exitoso(self):
        certificacion = self._crear_certificacion()
        actualizada = CertificacionExternaService.actualizar(
            certificacion_id=certificacion.pk, tipo='DIPLOMADO',
            nombre_programa='Nuevo nombre', institucion=certificacion.institucion,
            horas_certificadas=certificacion.horas_certificadas,
            fecha_inicio=certificacion.fecha_inicio, fecha_fin=certificacion.fecha_fin,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.nombre_programa, 'Nuevo nombre')

    def test_actualizar_certificacion_validada_falla(self):
        certificacion = self._crear_certificacion()
        documento = self._crear_documento_firma('Certificado de aprobación')
        CertificacionExternaService.adjuntar_certificado_aprobacion(
            certificacion.pk, documento.pk, ejecutor=self.ejecutor,
        )
        CertificacionExternaService.validar_horas(
            certificacion_id=certificacion.pk, horas_validadas=certificacion.horas_certificadas,
            validado_por_id=self.ejecutor.pk, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            CertificacionExternaService.actualizar(
                certificacion_id=certificacion.pk, tipo=certificacion.tipo,
                nombre_programa='otro', institucion=certificacion.institucion,
                horas_certificadas=certificacion.horas_certificadas,
                fecha_inicio=certificacion.fecha_inicio, fecha_fin=certificacion.fecha_fin,
                ejecutor=self.ejecutor,
            )

    def test_adjuntar_certificado_aprobacion_exitoso(self):
        certificacion = self._crear_certificacion()
        documento = self._crear_documento_firma('Certificado de aprobación 1')
        actualizada = CertificacionExternaService.adjuntar_certificado_aprobacion(
            certificacion.pk, documento.pk, ejecutor=self.ejecutor
        )
        self.assertEqual(actualizada.certificado_aprobacion_id, documento.pk)

    def test_adjuntar_certificado_aprobacion_sin_documento_falla(self):
        certificacion = self._crear_certificacion()
        with self.assertRaises(ValidationError):
            CertificacionExternaService.adjuntar_certificado_aprobacion(
                certificacion.pk, None, ejecutor=self.ejecutor
            )

    def test_validar_horas_exitoso_cumple_minimo(self):
        certificacion = self._crear_certificacion(horas_certificadas=150)
        documento = self._crear_documento_firma('Certificado de aprobación 2')
        CertificacionExternaService.adjuntar_certificado_aprobacion(
            certificacion.pk, documento.pk, ejecutor=self.ejecutor
        )
        validada = CertificacionExternaService.validar_horas(
            certificacion.pk, horas_validadas=130, validado_por_id=self.ejecutor.pk,
            ejecutor=self.ejecutor,
        )
        self.assertTrue(validada.cumple_horas)
        self.assertIsNotNone(validada.fecha_validacion)

    def test_validar_horas_no_cumple_minimo(self):
        certificacion = self._crear_certificacion(horas_certificadas=100)
        documento = self._crear_documento_firma('Certificado de aprobación 3')
        CertificacionExternaService.adjuntar_certificado_aprobacion(
            certificacion.pk, documento.pk, ejecutor=self.ejecutor
        )
        validada = CertificacionExternaService.validar_horas(
            certificacion.pk, horas_validadas=80, validado_por_id=self.ejecutor.pk,
            ejecutor=self.ejecutor,
        )
        self.assertFalse(validada.cumple_horas)

    def test_validar_horas_sin_certificado_aprobacion_falla(self):
        certificacion = self._crear_certificacion()
        with self.assertRaises(ValidationError):
            CertificacionExternaService.validar_horas(
                certificacion.pk, horas_validadas=130, validado_por_id=self.ejecutor.pk,
                ejecutor=self.ejecutor,
            )

    def test_validar_horas_dos_veces_falla(self):
        certificacion = self._crear_certificacion(horas_certificadas=150)
        documento = self._crear_documento_firma('Certificado de aprobación 4')
        CertificacionExternaService.adjuntar_certificado_aprobacion(
            certificacion.pk, documento.pk, ejecutor=self.ejecutor
        )
        CertificacionExternaService.validar_horas(
            certificacion.pk, horas_validadas=130, validado_por_id=self.ejecutor.pk,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            CertificacionExternaService.validar_horas(
                certificacion.pk, horas_validadas=140, validado_por_id=self.ejecutor.pk,
                ejecutor=self.ejecutor,
            )

    def test_eliminar_certificacion_no_validada_exitoso(self):
        certificacion = self._crear_certificacion()
        resultado = CertificacionExternaService.eliminar(certificacion.pk, ejecutor=self.ejecutor)
        self.assertTrue(resultado)
        self.assertFalse(
            CertificacionExternaService.listar().filter(pk=certificacion.pk).exists()
        )

    def test_eliminar_certificacion_validada_falla(self):
        certificacion = self._crear_certificacion(horas_certificadas=150)
        documento = self._crear_documento_firma('Certificado de aprobación 5')
        CertificacionExternaService.adjuntar_certificado_aprobacion(
            certificacion.pk, documento.pk, ejecutor=self.ejecutor
        )
        CertificacionExternaService.validar_horas(
            certificacion.pk, horas_validadas=130, validado_por_id=self.ejecutor.pk,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            CertificacionExternaService.eliminar(certificacion.pk, ejecutor=self.ejecutor)