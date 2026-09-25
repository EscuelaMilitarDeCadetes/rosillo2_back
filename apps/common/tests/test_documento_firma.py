import os

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import CommonFixturesMixin
from apps.common.services.documento_firma_service import DocumentoFirmaService


class DocumentoFirmaServiceTests(CommonFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.ruta_acta_v1 = self._crear_archivo_temporal('acta_v1.pdf', b'contenido acta v1')
        self.ruta_acta_v2 = self._crear_archivo_temporal('acta_v2.pdf', b'contenido acta v2')
        self.ruta_otro = self._crear_archivo_temporal('otro.pdf', b'contenido otro documento')

    def test_crear_documento_exitoso_es_version_1(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(documento.version, 1)
        self.assertEqual(documento.estado, 'BORRADOR')
        self.assertEqual(len(documento.hash_documento), 64)

    def test_crear_segundo_documento_mismo_tipo_incrementa_version(self):
        DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        segundo = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v2,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(segundo.version, 2)

    def test_crear_documento_asociado_a_objeto_generico(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
            objeto=self.objeto_generico,
        )
        self.assertEqual(documento.object_id, self.objeto_generico.pk)
        self.assertEqual(documento.objeto_relacionado, self.objeto_generico)

    def test_crear_documento_sin_objeto_deja_content_type_nulo(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        self.assertIsNone(documento.content_type)
        self.assertIsNone(documento.object_id)

    def test_habilitar_para_firma(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        habilitado = DocumentoFirmaService.habilitar_para_firma(documento.pk, ejecutor=self.ejecutor)
        self.assertEqual(habilitado.estado, 'EN_FIRMAS')
        self.assertTrue(habilitado.habilitado_firma)

    def test_marcar_rechazado(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        rechazado = DocumentoFirmaService.marcar_rechazado(documento.pk, ejecutor=self.ejecutor)
        self.assertEqual(rechazado.estado, 'RECHAZADO')
        self.assertFalse(rechazado.habilitado_firma)

    def test_marcar_firmado_completamente(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        firmado = DocumentoFirmaService.marcar_firmado_completamente(documento.pk, ejecutor=self.ejecutor)
        self.assertEqual(firmado.estado, 'FIRMADO')

    def test_no_se_puede_retroceder_un_documento_ya_firmado(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        DocumentoFirmaService.marcar_firmado_completamente(documento.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            DocumentoFirmaService.marcar_rechazado(documento.pk, ejecutor=self.ejecutor)

    def test_eliminar_documento_en_borrador_exitoso(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        resultado = DocumentoFirmaService.eliminar(documento.pk, ejecutor=self.ejecutor)
        self.assertTrue(resultado)

    def test_eliminar_documento_en_firmas_falla(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        DocumentoFirmaService.habilitar_para_firma(documento.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            DocumentoFirmaService.eliminar(documento.pk, ejecutor=self.ejecutor)

    def test_listar_por_tipo_documento(self):
        DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        resultados = DocumentoFirmaService.listar_por_tipo_documento(self.tipo_documento.pk)
        self.assertEqual(resultados.count(), 1)

    def test_obtener_ultima_version(self):
        DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        segundo = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v2,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        ultima = DocumentoFirmaService.obtener_ultima_version(self.tipo_documento.pk)
        self.assertEqual(ultima.pk, segundo.pk)

    def test_listar_habilitados_para_firma(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
        )
        DocumentoFirmaService.habilitar_para_firma(documento.pk, ejecutor=self.ejecutor)
        habilitados = DocumentoFirmaService.listar_habilitados_para_firma()
        self.assertEqual(habilitados.count(), 1)

    def test_listar_por_objeto(self):
        DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
            objeto=self.objeto_generico,
        )
        otro_objeto = self._crear_objeto_generico(nombre='Otra Facultad', abreviatura='OFAC')
        DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_otro,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
            objeto=otro_objeto,
        )
        resultados = DocumentoFirmaService.listar_por_objeto(self.objeto_generico)
        self.assertEqual(resultados.count(), 1)
        self.assertEqual(resultados.first().ruta_documento, self.ruta_acta_v1)
        
    def test_crear_documento_con_estado_firmado_para_carga_historica(self):
        documento = DocumentoFirmaService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento=self.ruta_acta_v1,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
            estado='FIRMADO',
        )
        self.assertEqual(documento.estado, 'FIRMADO')
    
    def test_crear_desde_archivo_escribe_en_disco_y_asocia_objeto(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        archivo = SimpleUploadedFile(
            'convocatoria.pdf', b'contenido pdf de prueba', content_type='application/pdf'
        )
        documento = DocumentoFirmaService.crear_desde_archivo(
            tipo_documento_id=self.tipo_documento.pk,
            archivo=archivo,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
            objeto=self.objeto_generico,
            carpeta='pruebas',
        )
        self.assertEqual(documento.estado, 'BORRADOR')
        self.assertEqual(documento.object_id, self.objeto_generico.pk)
        self.assertEqual(len(documento.hash_documento), 64)
        # El archivo debe existir físicamente en la ruta que quedó registrada.
        self.assertTrue(os.path.exists(documento.ruta_documento))
    
    def test_crear_desde_archivo_con_estado_firmado(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        archivo = SimpleUploadedFile(
            'historico.pdf', b'documento ya firmado en 2021', content_type='application/pdf'
        )
        documento = DocumentoFirmaService.crear_desde_archivo(
            tipo_documento_id=self.tipo_documento.pk,
            archivo=archivo,
            ip_creacion='127.0.0.1',
            ejecutor=self.ejecutor,
            estado='FIRMADO',
            carpeta='pruebas',
        )
        self.assertEqual(documento.estado, 'FIRMADO')
        
    def test_crear_desde_archivo_rechaza_no_pdf(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        archivo = SimpleUploadedFile('documento.docx', b'contenido', content_type='application/msword')
        with self.assertRaises(ValidationError):
            DocumentoFirmaService.crear_desde_archivo(
                tipo_documento_id=self.tipo_documento.pk,
                archivo=archivo,
                ip_creacion='127.0.0.1',
                ejecutor=self.ejecutor,
                carpeta='pruebas',
            )

    def test_crear_desde_archivo_rechaza_tamano_excesivo(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        archivo = SimpleUploadedFile(
            'grande.pdf', b'x' * 10, content_type='application/pdf'
        )
        archivo.size = 15_500_000  # simula >15MB (TAMANO_MAXIMO_PDF) sin escribir bytes reales
        with self.assertRaises(ValidationError):
            DocumentoFirmaService.crear_desde_archivo(
                tipo_documento_id=self.tipo_documento.pk,
                archivo=archivo,
                ip_creacion='127.0.0.1',
                ejecutor=self.ejecutor,
                carpeta='pruebas',
            )