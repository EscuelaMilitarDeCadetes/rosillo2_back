from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .base import CommonFixturesMixin
from apps.common.services.plantilla_documento_service import PlantillaDocumentoService
from apps.common.services.tipo_documento_service import TipoDocumentoService


class PlantillaDocumentoServiceTests(CommonFixturesMixin, TestCase):

    def test_crear_plantilla_exitoso(self):
        plantilla = PlantillaDocumentoService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento='/plantillas/acta_cierre.docx',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(plantilla.tipo_documento_id, self.tipo_documento.pk)
        self.assertTrue(plantilla.estado)

    def test_crear_plantilla_tipo_documento_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            PlantillaDocumentoService.crear(
                tipo_documento_id=999999,
                ruta_documento='/plantillas/x.docx',
                ejecutor=self.ejecutor,
            )

    def test_crear_plantilla_ruta_vacia_falla(self):
        with self.assertRaises(ValidationError):
            PlantillaDocumentoService.crear(
                tipo_documento_id=self.tipo_documento.pk,
                ruta_documento='   ',
                ejecutor=self.ejecutor,
            )

    def test_crear_segunda_plantilla_para_mismo_tipo_documento_falla(self):
        PlantillaDocumentoService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento='/plantillas/v1.docx',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            PlantillaDocumentoService.crear(
                tipo_documento_id=self.tipo_documento.pk,
                ruta_documento='/plantillas/v2.docx',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_plantilla_exitoso(self):
        plantilla = PlantillaDocumentoService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento='/plantillas/v1.docx',
            ejecutor=self.ejecutor,
        )
        actualizada = PlantillaDocumentoService.actualizar(
            plantilla_id=plantilla.pk,
            ejecutor=self.ejecutor,
            ruta_documento='/plantillas/v1_corregida.docx',
        )
        self.assertEqual(actualizada.ruta_documento, '/plantillas/v1_corregida.docx')

    def test_desactivar_plantilla(self):
        plantilla = PlantillaDocumentoService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento='/plantillas/v1.docx',
            ejecutor=self.ejecutor,
        )
        desactivada = PlantillaDocumentoService.desactivar(plantilla.pk, ejecutor=self.ejecutor)
        self.assertFalse(desactivada.estado)

    def test_obtener_por_tipo_documento(self):
        PlantillaDocumentoService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento='/plantillas/v1.docx',
            ejecutor=self.ejecutor,
        )
        encontrada = PlantillaDocumentoService.obtener_por_tipo_documento(self.tipo_documento.pk)
        self.assertIsNotNone(encontrada)

    def test_obtener_por_tipo_documento_desactivada_no_aparece(self):
        plantilla = PlantillaDocumentoService.crear(
            tipo_documento_id=self.tipo_documento.pk,
            ruta_documento='/plantillas/v1.docx',
            ejecutor=self.ejecutor,
        )
        PlantillaDocumentoService.desactivar(plantilla.pk, ejecutor=self.ejecutor)
        encontrada = PlantillaDocumentoService.obtener_por_tipo_documento(self.tipo_documento.pk)
        self.assertIsNone(encontrada)