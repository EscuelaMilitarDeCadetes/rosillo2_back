# apps/investigacion_formal/tests/test_objetivo_x_punto.py
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.objetivos_service import ObjetivosService
from apps.investigacion_formal.services.objetivo_x_punto_service import ObjetivoXPuntoService


class ObjetivoXPuntoServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proyecto = self._crear_proyecto()
        self.objetivo = ObjetivosService.crear_objetivo_especifico(
            proyecto_id=self.proyecto.pk,
            objetivo='Objetivo con punto de control',
            ejecutor=self.ejecutor,
        )

    def test_crear_objetivo_x_punto_crea_punto_control_nuevo(self):
        vinculo = ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Entrega de informe mensual',
            peso=25,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(vinculo.punto_control.control, 'Entrega de informe mensual')
        self.assertEqual(vinculo.avance, 0)
        self.assertTrue(vinculo.estado)

    def test_crear_objetivo_x_punto_reutiliza_punto_control_existente(self):
        primero = ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Punto Compartido',
            peso=50,
            ejecutor=self.ejecutor,
        )
        otro_objetivo = ObjetivosService.crear_objetivo_especifico(
            proyecto_id=self.proyecto.pk,
            objetivo='Segundo objetivo',
            ejecutor=self.ejecutor,
        )
        segundo = ObjetivoXPuntoService.crear(
            objetivo_id=otro_objetivo.pk,
            control='Punto Compartido',
            peso=50,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(primero.punto_control_id, segundo.punto_control_id)

    def test_crear_objetivo_x_punto_vinculo_duplicado_falla(self):
        vinculo = ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Punto Único',
            peso=30,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ObjetivoXPuntoService.crear(
                objetivo_id=self.objetivo.pk,
                control='Punto Único',
                peso=30,
                ejecutor=self.ejecutor,
            )

    def test_agregar_avance_desactiva_registro_anterior_y_crea_uno_nuevo(self):
        vinculo_inicial = ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Seguimiento mensual',
            peso=100,
            ejecutor=self.ejecutor,
        )
        nuevo, es_correccion = ObjetivoXPuntoService.agregar_avance(
            punto_control_id=vinculo_inicial.punto_control_id,
            descripcion_avance='Avance del primer mes',
            avance=25,
            mes_avance='ENERO',
            anio_avance=2024,
            ejecutor=self.ejecutor,
        )
        vinculo_inicial.refresh_from_db()
        self.assertFalse(vinculo_inicial.estado)
        self.assertTrue(nuevo.estado)
        self.assertEqual(nuevo.avance, 25)
        self.assertEqual(nuevo.objetivo_id, vinculo_inicial.objetivo_id)

        nuevo.punto_control.refresh_from_db()
        self.assertEqual(nuevo.punto_control.completado, 25)

    def test_agregar_avance_fuera_de_rango_falla(self):
        vinculo = ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Punto con avance inválido',
            peso=100,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ObjetivoXPuntoService.agregar_avance(
                punto_control_id=vinculo.punto_control_id,
                descripcion_avance='Avance imposible',
                avance=150,
                mes_avance='FEBRERO',
                anio_avance=2024,
                ejecutor=self.ejecutor,
            )

    def test_agregar_avance_mes_invalido_falla(self):
        vinculo = ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Punto con mes inválido',
            peso=100,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ObjetivoXPuntoService.agregar_avance(
                punto_control_id=vinculo.punto_control_id,
                descripcion_avance='Avance con mes malo',
                avance=30,
                mes_avance='MESINVENTADO',
                anio_avance=2024,
                ejecutor=self.ejecutor,
            )

    def test_eliminar_objetivo_x_punto_soft_delete(self):
        vinculo = ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Punto a desactivar',
            peso=10,
            ejecutor=self.ejecutor,
        )
        ObjetivoXPuntoService.eliminar(vinculo.pk, ejecutor=self.ejecutor)
        vinculo.refresh_from_db()
        self.assertFalse(vinculo.estado)

    def test_listar_por_proyecto(self):
        ObjetivoXPuntoService.crear(
            objetivo_id=self.objetivo.pk,
            control='Punto de listado',
            peso=10,
            ejecutor=self.ejecutor,
        )
        resultado = ObjetivoXPuntoService.listar_por_proyecto(self.proyecto.pk)
        self.assertEqual(resultado.count(), 1)