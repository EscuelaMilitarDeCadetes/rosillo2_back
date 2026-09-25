from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .base import CommonFixturesMixin
from apps.usuarios.models import Usuario
from apps.common.services.documento_firma_service import DocumentoFirmaService
from apps.common.services.documento_firmante_service import DocumentoFirmanteService


class DocumentoFirmanteServiceTests(CommonFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.ruta_acta_v1 = self._crear_archivo_temporal('acta_v1.pdf', b'contenido acta v1')
        self.documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        self.tercer_usuario = Usuario.objects.create_user(
            username='gerente@esmic.edu.co',
            email='gerente@esmic.edu.co',
            password='gerente123',
        )

    def test_asignar_firmante_exitoso(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(firmante.estado, 'PENDIENTE')
        self.assertEqual(firmante.orden, 1)

    def test_asignar_firmante_documento_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            DocumentoFirmanteService.asignar_firmante(
                documento_firma_id=999999,
                usuario_id=self.otro_usuario.pk,
                orden=1,
                ejecutor=self.ejecutor,
            )

    def test_asignar_firmante_orden_invalido_falla(self):
        with self.assertRaises(ValidationError):
            DocumentoFirmanteService.asignar_firmante(
                documento_firma_id=self.documento.pk,
                usuario_id=self.otro_usuario.pk,
                orden=0,
                ejecutor=self.ejecutor,
            )

    def test_asignar_firmante_duplicado_falla(self):
        DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            DocumentoFirmanteService.asignar_firmante(
                documento_firma_id=self.documento.pk,
                usuario_id=self.otro_usuario.pk,
                orden=2,
                ejecutor=self.ejecutor,
            )

    def test_asignar_firmantes_en_orden(self):
        firmantes = DocumentoFirmanteService.asignar_firmantes(
            documento_firma_id=self.documento.pk,
            usuarios_ids_en_orden=[self.otro_usuario.pk, self.tercer_usuario.pk],
            ejecutor=self.ejecutor,
        )
        self.assertEqual(len(firmantes), 2)
        self.assertEqual(firmantes[0].orden, 1)
        self.assertEqual(firmantes[1].orden, 2)

    def test_firmar_exitoso_marca_documento_firmado_si_era_el_ultimo(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        DocumentoFirmanteService.generar_codigo_verificacion(firmante.pk, ejecutor=self.ejecutor)
        firmante.refresh_from_db()
        firmado = DocumentoFirmanteService.firmar(
            documento_firmante_id=firmante.pk,
            codigo_verificacion=firmante.codigo_verificacion,
            ip_firma='127.0.0.1',
            ruta_firma='/firmas/firma1.png',
            ejecutor=self.otro_usuario,
        )
        self.assertEqual(firmado.estado, 'FIRMADO')
        self.documento.refresh_from_db()
        self.assertEqual(self.documento.estado, 'FIRMADO')

    def test_firmar_no_marca_documento_firmado_si_faltan_firmantes(self):
        firmante1 = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.tercer_usuario.pk,
            orden=2,
            ejecutor=self.ejecutor,
        )
        DocumentoFirmanteService.generar_codigo_verificacion(firmante1.pk, ejecutor=self.ejecutor)
        firmante1.refresh_from_db()
        DocumentoFirmanteService.firmar(
            documento_firmante_id=firmante1.pk,
            codigo_verificacion=firmante1.codigo_verificacion,
            ip_firma='127.0.0.1',
            ruta_firma='/firmas/firma1.png',
            ejecutor=self.otro_usuario,
        )
        self.documento.refresh_from_db()
        self.assertNotEqual(self.documento.estado, 'FIRMADO')

    def test_firmar_con_codigo_incorrecto_falla(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        DocumentoFirmanteService.generar_codigo_verificacion(firmante.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            DocumentoFirmanteService.firmar(
                documento_firmante_id=firmante.pk,
                codigo_verificacion='000000',
                ip_firma='127.0.0.1',
                ruta_firma='/firmas/firma1.png',
                ejecutor=self.otro_usuario,
            )

    def test_firmar_dos_veces_falla(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        DocumentoFirmanteService.generar_codigo_verificacion(firmante.pk, ejecutor=self.ejecutor)
        firmante.refresh_from_db()
        DocumentoFirmanteService.firmar(
            documento_firmante_id=firmante.pk,
            codigo_verificacion=firmante.codigo_verificacion,
            ip_firma='127.0.0.1',
            ruta_firma='/firmas/firma1.png',
            ejecutor=self.otro_usuario,
        )
        with self.assertRaises(ValidationError):
            DocumentoFirmanteService.firmar(
                documento_firmante_id=firmante.pk,
                codigo_verificacion=firmante.codigo_verificacion,
                ip_firma='127.0.0.1',
                ruta_firma='/firmas/firma1.png',
                ejecutor=self.otro_usuario,
            )

    def test_rechazar_exitoso_marca_documento_rechazado(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        rechazado = DocumentoFirmanteService.rechazar(
            documento_firmante_id=firmante.pk,
            motivo_rechazo='El documento tiene datos incorrectos',
            ejecutor=self.otro_usuario,
        )
        self.assertEqual(rechazado.estado, 'RECHAZADO')
        self.documento.refresh_from_db()
        self.assertEqual(self.documento.estado, 'RECHAZADO')

    def test_rechazar_sin_motivo_falla(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            DocumentoFirmanteService.rechazar(
                documento_firmante_id=firmante.pk, motivo_rechazo='', ejecutor=self.otro_usuario
            )

    def test_listar_por_documento_respeta_orden(self):
        DocumentoFirmanteService.asignar_firmantes(
            documento_firma_id=self.documento.pk,
            usuarios_ids_en_orden=[self.tercer_usuario.pk, self.otro_usuario.pk],
            ejecutor=self.ejecutor,
        )
        firmantes = list(DocumentoFirmanteService.listar_por_documento(self.documento.pk))
        self.assertEqual(firmantes[0].usuario_id, self.tercer_usuario.pk)
        self.assertEqual(firmantes[1].usuario_id, self.otro_usuario.pk)

    def test_listar_pendientes_por_usuario(self):
        DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        pendientes = DocumentoFirmanteService.listar_pendientes_por_usuario(self.otro_usuario.pk)
        self.assertEqual(pendientes.count(), 1)

    def test_obtener_siguiente_turno(self):
        firmante1 = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.tercer_usuario.pk,
            orden=2,
            ejecutor=self.ejecutor,
        )
        siguiente = DocumentoFirmanteService.obtener_siguiente_turno(self.documento.pk)
        self.assertEqual(siguiente.pk, firmante1.pk)

    def test_eliminar_firmante_pendiente_exitoso(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        resultado = DocumentoFirmanteService.eliminar(firmante.pk, ejecutor=self.ejecutor)
        self.assertTrue(resultado)

    def test_eliminar_firmante_ya_firmado_falla(self):
        firmante = DocumentoFirmanteService.asignar_firmante(
            documento_firma_id=self.documento.pk,
            usuario_id=self.otro_usuario.pk,
            orden=1,
            ejecutor=self.ejecutor,
        )
        DocumentoFirmanteService.generar_codigo_verificacion(firmante.pk, ejecutor=self.ejecutor)
        firmante.refresh_from_db()
        DocumentoFirmanteService.firmar(
            documento_firmante_id=firmante.pk,
            codigo_verificacion=firmante.codigo_verificacion,
            ip_firma='127.0.0.1',
            ruta_firma='/firmas/firma1.png',
            ejecutor=self.otro_usuario,
        )
        with self.assertRaises(ValidationError):
            DocumentoFirmanteService.eliminar(firmante.pk, ejecutor=self.ejecutor)