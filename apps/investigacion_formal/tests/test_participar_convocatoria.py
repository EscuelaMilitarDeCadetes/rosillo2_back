# apps/investigacion_formal/tests/test_participar_convocatoria.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.models import Proyecto, Calificacion, Monto
from apps.investigacion_formal.services.proyecto_x_convocatoria_service import (
    ProyectoXConvocatoriaService,
)
from apps.common.models import TipoDocumento, DocumentoFirma
from apps.institucional.models import Gerente


def _pdf(nombre="documento.pdf"):
    return SimpleUploadedFile(nombre, b"%PDF-1.4 contenido de prueba", content_type="application/pdf")


def _no_pdf(nombre="documento.docx"):
    return SimpleUploadedFile(
        nombre, b"contenido cualquiera",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


class ParticiparConvocatoriaTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        # Sin seeds: los TipoDocumento que el orquestador resuelve por nombre
        # se crean aquí explícitamente, igual que cualquier otro fixture.
        self.tipo_doc_proyecto = TipoDocumento.objects.create(
            nombre_documento="Documento de Proyecto", grupo="proyecto",
        )
        self.tipo_doc_carta = TipoDocumento.objects.create(
            nombre_documento="Carta de Compromiso", grupo="proyecto",
        )
        self.tipo_doc_alianza = TipoDocumento.objects.create(
            nombre_documento="Documento de Alianza", grupo="proyecto",
        )
        self.fase_1 = self._crear_tipo_calificacion(nombre="Fase 1", orden=1)
        self.fase_2 = self._crear_tipo_calificacion(nombre="Fase 2", orden=2)
        self.convocatoria = self._crear_convocatoria(interno=True)

    def _participar(self, **overrides):
        datos = dict(
            convocatoria_id=self.convocatoria.pk,
            titulo="Proyecto participación exitosa",
            alianza=False,
            financiado=True,
            unidad_ejecutora="ING",
            linea_investigacion="Tecnología",
            valor_solicitado=5_000_000,
            doc_proyecto=_pdf("proyecto.pdf"),
            doc_carta=_pdf("carta.pdf"),
            doc_alianza=_pdf("alianza.pdf"),
            ip_creacion="127.0.0.1",
            ejecutor=self.ejecutor,
        )
        datos.update(overrides)
        return ProyectoXConvocatoriaService.participar_convocatoria(**datos)

    # ------------------------------------------------------------------
    # Caso feliz completo
    # ------------------------------------------------------------------
    def test_participar_convocatoria_exitoso(self):
        vinculo = self._participar()

        self.assertTrue(vinculo.estado)
        self.assertEqual(vinculo.convocatoria_id, self.convocatoria.pk)

        proyecto = vinculo.proyecto
        self.assertTrue(proyecto.interno)
        self.assertEqual(proyecto.usuario_id, self.ejecutor.pk)
        self.assertEqual(proyecto.gerente_id, self.gerente.pk)  # resuelto automáticamente
        self.assertTrue(proyecto.financiado)

        monto = Monto.objects.get(proyecto=proyecto)
        self.assertEqual(monto.solicitado, 5_000_000)

        documentos = DocumentoFirma.objects.filter(
            content_type__model="proyecto", object_id=proyecto.pk,
        )
        self.assertEqual(documentos.count(), 3)

        calificaciones = Calificacion.objects.filter(aplicar=vinculo)
        self.assertEqual(calificaciones.count(), 2)  # una por cada TipoCalificacion activo
        self.assertTrue(
            calificaciones.filter(fase=self.fase_1).exists()
            and calificaciones.filter(fase=self.fase_2).exists()
        )

    # ------------------------------------------------------------------
    # Documentos opcionales realmente opcionales; el monto SIEMPRE se crea
    # ------------------------------------------------------------------
    def test_participar_convocatoria_solo_documento_obligatorio(self):
        vinculo = self._participar(
            titulo="Proyecto sin doc opcionales",
            financiado=False,
            valor_solicitado=0,
            doc_carta=None,
            doc_alianza=None,
        )
        proyecto = vinculo.proyecto

        monto = Monto.objects.get(proyecto=proyecto)
        self.assertEqual(monto.solicitado, 0)

        documentos = DocumentoFirma.objects.filter(
            content_type__model="proyecto", object_id=proyecto.pk,
        )
        self.assertEqual(documentos.count(), 1)  # solo doc_proyecto

    # ------------------------------------------------------------------
    # doc_proyecto es obligatorio
    # ------------------------------------------------------------------
    def test_participar_convocatoria_sin_doc_proyecto_falla(self):
        proyectos_antes = Proyecto.objects.count()
        with self.assertRaises(ValidationError):
            self._participar(titulo="No debería crearse", doc_proyecto=None)
        self.assertEqual(Proyecto.objects.count(), proyectos_antes)

    # ------------------------------------------------------------------
    # Sin Gerente vigente no se puede asignar responsable -> rollback total
    # ------------------------------------------------------------------
    def test_participar_convocatoria_sin_gerente_vigente_falla(self):
        Gerente.objects.update(estado=False)  # desactiva el único gerente vigente del fixture
        proyectos_antes = Proyecto.objects.count()
        montos_antes = Monto.objects.count()

        with self.assertRaises(ValidationError):
            self._participar(titulo="No debería crearse sin gerente")

        self.assertEqual(Proyecto.objects.count(), proyectos_antes)
        self.assertEqual(Monto.objects.count(), montos_antes)

    # ------------------------------------------------------------------
    # Falla de validación PDF a mitad de la orquestación -> rollback completo
    # (Proyecto y Monto ya se habían creado antes de llegar al documento
    # inválido; @transaction.atomic debe deshacerlos igual).
    # ------------------------------------------------------------------
    def test_participar_convocatoria_archivo_no_pdf_falla_y_revierte_todo(self):
        proyectos_antes = Proyecto.objects.count()
        montos_antes = Monto.objects.count()
        documentos_antes = DocumentoFirma.objects.count()

        with self.assertRaises(ValidationError):
            self._participar(
                titulo="No debería persistir nada",
                doc_proyecto=_no_pdf("proyecto.docx"),
            )

        self.assertEqual(Proyecto.objects.count(), proyectos_antes)
        self.assertEqual(Monto.objects.count(), montos_antes)
        self.assertEqual(DocumentoFirma.objects.count(), documentos_antes)

    # ------------------------------------------------------------------
    # Convocatoria inactiva -> falla en ProyectoXConvocatoriaService.crear(),
    # que ya se reutiliza dentro del orquestador; el rollback debe alcanzar
    # también al Proyecto, Monto y documentos ya creados en pasos previos.
    # ------------------------------------------------------------------
    def test_participar_convocatoria_en_convocatoria_cerrada_falla_y_revierte_todo(self):
        self.convocatoria.estado = False
        self.convocatoria.save(update_fields=['estado'])

        proyectos_antes = Proyecto.objects.count()
        montos_antes = Monto.objects.count()

        with self.assertRaises(ValidationError):
            self._participar(titulo="No debería persistir con convocatoria cerrada")

        self.assertEqual(Proyecto.objects.count(), proyectos_antes)
        self.assertEqual(Monto.objects.count(), montos_antes)