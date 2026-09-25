# apps/investigacion_formativa/tests/test_banco_ideas.py

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.banco_ideas_service import BancoIdeasService


class BancoIdeasServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def test_crear_idea_exitosa(self):
        idea = BancoIdeasService.crear(
            facultad_id=self.facultad.pk,
            idea='Nueva idea de investigación',
            descripcion='Descripción de la idea',
            linea_investigacion='Inteligencia Artificial',
            palabras_clave='IA, machine learning',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(idea.estado, 'DISPONIBLE')

    def test_crear_idea_titulo_duplicado_en_misma_facultad_falla(self):
        with self.assertRaises(ValidationError):
            BancoIdeasService.crear(
                facultad_id=self.facultad.pk,
                idea='idea semilla de prueba',  # coincide (case-insensitive) con self.idea de la fixture
                descripcion='Otra descripción',
                linea_investigacion='Otra línea',
                palabras_clave='otra',
                ejecutor=self.ejecutor,
            )

    def test_crear_idea_titulo_vacio_falla(self):
        with self.assertRaises(ValidationError):
            BancoIdeasService.crear(
                facultad_id=self.facultad.pk,
                idea='',
                descripcion='Descripción',
                linea_investigacion='Línea',
                palabras_clave='clave',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_idea_exitosa(self):
        idea = self._crear_banco_idea(idea='Idea a actualizar')
        actualizada = BancoIdeasService.actualizar(
            idea_id=idea.pk,
            descripcion='Descripción actualizada',
            linea_investigacion='Línea actualizada',
            palabras_clave='nuevas, palabras',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizada.descripcion, 'Descripción actualizada')

    def test_separar_idea_disponible_exitoso(self):
        idea = self._crear_banco_idea(idea='Idea a separar')
        separada = BancoIdeasService.separar(idea.pk, ejecutor=self.ejecutor)
        self.assertEqual(separada.estado, 'SEPARADA')

    def test_separar_idea_ya_separada_falla(self):
        idea = self._crear_banco_idea(idea='Idea ya separada', estado='SEPARADA')
        with self.assertRaises(ValidationError):
            BancoIdeasService.separar(idea.pk, ejecutor=self.ejecutor)

    def test_tomar_idea_disponible_exitoso(self):
        idea = self._crear_banco_idea(idea='Idea a tomar')
        tomada = BancoIdeasService.tomar(idea.pk, ejecutor=self.ejecutor)
        self.assertEqual(tomada.estado, 'TOMADA')

    def test_tomar_idea_ya_tomada_falla(self):
        idea = self._crear_banco_idea(idea='Idea ya tomada', estado='TOMADA')
        with self.assertRaises(ValidationError):
            BancoIdeasService.tomar(idea.pk, ejecutor=self.ejecutor)

    def test_liberar_idea_separada_exitoso(self):
        idea = self._crear_banco_idea(idea='Idea a liberar', estado='SEPARADA')
        liberada = BancoIdeasService.liberar(idea.pk, ejecutor=self.ejecutor)
        self.assertEqual(liberada.estado, 'DISPONIBLE')

    def test_liberar_idea_disponible_falla(self):
        idea = self._crear_banco_idea(idea='Idea aún disponible')
        with self.assertRaises(ValidationError):
            BancoIdeasService.liberar(idea.pk, ejecutor=self.ejecutor)

    def test_eliminar_idea_disponible_exitoso(self):
        idea = self._crear_banco_idea(idea='Idea a eliminar')
        resultado = BancoIdeasService.eliminar(idea.pk, ejecutor=self.ejecutor)
        self.assertEqual(resultado.estado, 'ELIMINADA')
        self.assertTrue(BancoIdeasService.listar().filter(pk=idea.pk).exists())  # sigue en el historial
        self.assertFalse(
            BancoIdeasService.listar_disponibles().filter(pk=idea.pk).exists()
        )

    def test_eliminar_idea_tomada_falla(self):
        idea = self._crear_banco_idea(idea='Idea comprometida', estado='TOMADA')
        with self.assertRaises(ValidationError):
            BancoIdeasService.eliminar(idea.pk, ejecutor=self.ejecutor)

    def test_listar_disponibles_por_facultad(self):
        self._crear_banco_idea(idea='Idea disponible extra')
        tomada = self._crear_banco_idea(idea='Idea ya tomada extra', estado='TOMADA')
        disponibles = BancoIdeasService.listar_disponibles_por_facultad(self.facultad.pk)
        ids_disponibles = set(disponibles.values_list('pk', flat=True))
        self.assertIn(self.idea.pk, ids_disponibles)
        self.assertNotIn(tomada.pk, ids_disponibles)