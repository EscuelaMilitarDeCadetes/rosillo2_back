from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .base import CommonFixturesMixin
from apps.common.services.aprobacion_service import AprobacionService


class AprobacionServiceTests(CommonFixturesMixin, TestCase):

    def test_crear_aprobacion_exitoso(self):
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(aprobacion.estado, 'PENDIENTE')

    def test_crear_aprobacion_sin_usuario_revisor_falla(self):
        with self.assertRaises(ValidationError):
            AprobacionService.crear(
                usuario_revisor_id=None,
                tipo_documento_id=self.tipo_documento.pk,
                id_documento=101,
                ejecutor=self.ejecutor,
            )

    def test_crear_aprobacion_tipo_documento_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            AprobacionService.crear(
                usuario_revisor_id=self.otro_usuario.pk,
                tipo_documento_id=999999,
                id_documento=101,
                ejecutor=self.ejecutor,
            )

    def test_crear_aprobacion_estado_invalido_falla(self):
        with self.assertRaises(ValidationError):
            AprobacionService.crear(
                usuario_revisor_id=self.otro_usuario.pk,
                tipo_documento_id=self.tipo_documento.pk,
                id_documento=101,
                ejecutor=self.ejecutor,
                estado='EN_REVISION',
            )

    def test_crear_aprobacion_duplicada_falla(self):
        AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            AprobacionService.crear(
                usuario_revisor_id=self.otro_usuario.pk,
                tipo_documento_id=self.tipo_documento.pk,
                id_documento=101,
                ejecutor=self.ejecutor,
            )

    def test_aprobar_exitoso(self):
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        aprobada = AprobacionService.aprobar(
            aprobacion.pk, ejecutor=self.otro_usuario, observacion='Todo en orden'
        )
        self.assertEqual(aprobada.estado, 'APROBADO')
        self.assertEqual(aprobada.observacion, 'Todo en orden')

    def test_rechazar_exitoso(self):
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        rechazada = AprobacionService.rechazar(
            aprobacion.pk, ejecutor=self.otro_usuario, observacion='Falta la firma del gerente'
        )
        self.assertEqual(rechazada.estado, 'RECHAZADO')

    def test_rechazar_sin_observacion_falla(self):
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            AprobacionService.rechazar(aprobacion.pk, ejecutor=self.otro_usuario, observacion='   ')

    def test_listar_pendientes_por_revisor(self):
        AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        pendientes = AprobacionService.listar_pendientes(usuario_revisor_id=self.otro_usuario.pk)
        self.assertEqual(pendientes.count(), 1)

    def test_listar_por_documento(self):
        AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        resultados = AprobacionService.listar_por_documento(self.tipo_documento.pk, 101)
        self.assertEqual(resultados.count(), 1)

    def test_obtener_ultima_por_documento(self):
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=self.otro_usuario.pk,
            tipo_documento_id=self.tipo_documento.pk,
            id_documento=101,
            ejecutor=self.ejecutor,
        )
        ultima = AprobacionService.obtener_ultima_por_documento(self.tipo_documento.pk, 101)
        self.assertEqual(ultima.pk, aprobacion.pk)