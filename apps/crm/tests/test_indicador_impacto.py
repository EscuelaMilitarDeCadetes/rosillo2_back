from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import CrmFixturesMixin
from apps.crm.services.entidad_externa_service import EntidadExternaService
from apps.crm.services.indicador_impacto_service import IndicadorImpactoService


class IndicadorImpactoServiceTests(CrmFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proyecto = self._crear_proyecto('Proyecto Alfa')

    def test_crear_indicador_exitoso(self):
        indicador = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Artículos publicados',
            valor_proyectado=10,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(indicador.kpi_nombre, 'Artículos publicados')
        self.assertEqual(indicador.valor_proyectado, 10)
        self.assertEqual(indicador.valor_real, 0)  # default del modelo

    def test_crear_indicador_con_valor_real_inicial(self):
        indicador = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Estudiantes vinculados',
            valor_proyectado=20,
            valor_real=5,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(indicador.valor_real, 5)

    def test_crear_indicador_kpi_duplicado_para_mismo_proyecto_falla(self):
        IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Artículos publicados',
            valor_proyectado=10,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.crear(
                proyecto_id=self.proyecto.pk,
                kpi_nombre='artículos publicados',  # case-insensitive
                valor_proyectado=15,
                ejecutor=self.ejecutor,
            )

    def test_crear_indicador_mismo_kpi_en_proyecto_distinto_exitoso(self):
        otro_proyecto = self._crear_proyecto('Proyecto Beta')
        IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Artículos publicados',
            valor_proyectado=10,
            ejecutor=self.ejecutor,
        )
        indicador2 = IndicadorImpactoService.crear(
            proyecto_id=otro_proyecto.pk,
            kpi_nombre='Artículos publicados',
            valor_proyectado=8,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(indicador2.kpi_nombre, 'Artículos publicados')

    def test_crear_indicador_proyecto_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.crear(
                proyecto_id=999999,
                kpi_nombre='KPI inexistente',
                valor_proyectado=1,
                ejecutor=self.ejecutor,
            )

    def test_crear_indicador_sin_proyecto_falla(self):
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.crear(
                proyecto_id=None,
                kpi_nombre='KPI sin proyecto',
                valor_proyectado=1,
                ejecutor=self.ejecutor,
            )

    def test_crear_indicador_valor_proyectado_no_numerico_falla(self):
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.crear(
                proyecto_id=self.proyecto.pk,
                kpi_nombre='KPI inválido',
                valor_proyectado='no-es-numero',
                ejecutor=self.ejecutor,
            )

    def test_crear_indicador_kpi_nombre_vacio_falla(self):
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.crear(
                proyecto_id=self.proyecto.pk,
                kpi_nombre='   ',
                valor_proyectado=1,
                ejecutor=self.ejecutor,
            )

    def test_actualizar_indicador_exitoso(self):
        indicador = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Patentes',
            valor_proyectado=2,
            ejecutor=self.ejecutor,
        )
        actualizado = IndicadorImpactoService.actualizar(
            indicador_id=indicador.pk,
            ejecutor=self.ejecutor,
            valor_proyectado=3,
        )
        self.assertEqual(actualizado.valor_proyectado, 3)
        self.assertEqual(actualizado.kpi_nombre, 'Patentes')  # no cambió

    def test_actualizar_indicador_kpi_duplicado_con_otro_falla(self):
        IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Patentes',
            valor_proyectado=2,
            ejecutor=self.ejecutor,
        )
        indicador2 = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Publicaciones',
            valor_proyectado=5,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.actualizar(
                indicador_id=indicador2.pk,
                ejecutor=self.ejecutor,
                kpi_nombre='Patentes',
            )

    def test_actualizar_valor_real_no_modifica_valor_proyectado(self):
        indicador = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Estudiantes vinculados',
            valor_proyectado=20,
            ejecutor=self.ejecutor,
        )
        actualizado = IndicadorImpactoService.actualizar_valor_real(
            indicador_id=indicador.pk,
            nuevo_valor_real=12,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.valor_real, 12)
        self.assertEqual(actualizado.valor_proyectado, 20)  # intacto
        self.assertEqual(actualizado.kpi_nombre, 'Estudiantes vinculados')  # intacto

    def test_actualizar_valor_real_no_numerico_falla(self):
        indicador = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Estudiantes vinculados',
            valor_proyectado=20,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.actualizar_valor_real(
                indicador_id=indicador.pk,
                nuevo_valor_real='doce',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_valor_real_sin_valor_falla(self):
        """
        Cubre el bug corregido en el service: antes, omitir `valor_real`
        (None) se colaba hasta el modelo (FloatField no nullable) y
        producía un IntegrityError/500 en vez de un ValidationError/400.
        """
        indicador = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Estudiantes vinculados',
            valor_proyectado=20,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            IndicadorImpactoService.actualizar_valor_real(
                indicador_id=indicador.pk,
                nuevo_valor_real=None,
                ejecutor=self.ejecutor,
            )
        # El valor_real original no debe haberse tocado tras el intento fallido
        indicador.refresh_from_db()
        self.assertEqual(indicador.valor_real, 0)

    def test_eliminar_indicador_exitoso(self):
        indicador = IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='Eventos realizados',
            valor_proyectado=4,
            ejecutor=self.ejecutor,
        )
        resultado = IndicadorImpactoService.eliminar(indicador.pk, ejecutor=self.ejecutor)
        self.assertTrue(resultado)
        self.assertFalse(
            IndicadorImpactoService.listar().filter(pk=indicador.pk).exists()
        )

    def test_listar_por_proyecto(self):
        IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='KPI 1',
            valor_proyectado=1,
            ejecutor=self.ejecutor,
        )
        otro_proyecto = self._crear_proyecto('Proyecto Beta')
        IndicadorImpactoService.crear(
            proyecto_id=otro_proyecto.pk,
            kpi_nombre='KPI 2',
            valor_proyectado=2,
            ejecutor=self.ejecutor,
        )
        indicadores = IndicadorImpactoService.listar_por_proyecto(self.proyecto.pk)
        self.assertEqual(indicadores.count(), 1)
        self.assertEqual(indicadores.first().kpi_nombre, 'KPI 1')

    def test_obtener_por_proyecto_y_kpi(self):
        IndicadorImpactoService.crear(
            proyecto_id=self.proyecto.pk,
            kpi_nombre='KPI Único',
            valor_proyectado=7,
            ejecutor=self.ejecutor,
        )
        encontrado = IndicadorImpactoService.obtener_por_proyecto_y_kpi(
            self.proyecto.pk, 'kpi único'
        )
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.valor_proyectado, 7)