from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .base import CrmFixturesMixin
from apps.crm.services.entidad_externa_service import EntidadExternaService
from apps.crm.services.interaccion_service import InteraccionService


class EntidadExternaServiceTests(CrmFixturesMixin, TestCase):

    def test_crear_entidad_exitoso(self):
        entidad = EntidadExternaService.crear(
            nombre='Universidad Nacional',
            sector='Educación',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(entidad.nombre, 'Universidad Nacional')
        self.assertEqual(entidad.tipo_relacion, 'COOPERANTE')

    def test_crear_entidad_tipo_relacion_invalido_falla(self):
        with self.assertRaises(ValidationError):
            EntidadExternaService.crear(
                nombre='Fundación X',
                sector='ONG',
                pais='Colombia',
                tipo_relacion='PATROCINADOR',  # no es un valor válido
                ejecutor=self.ejecutor,
            )

    def test_crear_entidad_nombre_vacio_falla(self):
        with self.assertRaises(ValidationError):
            EntidadExternaService.crear(
                nombre='   ',
                sector='Educación',
                pais='Colombia',
                tipo_relacion='FINANCIADOR',
                ejecutor=self.ejecutor,
            )

    def test_crear_entidad_sector_vacio_falla(self):
        with self.assertRaises(ValidationError):
            EntidadExternaService.crear(
                nombre='Universidad Nacional',
                sector='',
                pais='Colombia',
                tipo_relacion='FINANCIADOR',
                ejecutor=self.ejecutor,
            )

    def test_crear_entidad_pais_vacio_falla(self):
        with self.assertRaises(ValidationError):
            EntidadExternaService.crear(
                nombre='Universidad Nacional',
                sector='Educación',
                pais='',
                tipo_relacion='FINANCIADOR',
                ejecutor=self.ejecutor,
            )

    def test_crear_entidad_permite_nombres_duplicados_en_paises_distintos(self):
        # Decisión institucional: no se fuerza unicidad de nombre, ya que
        # pueden existir dos instituciones homónimas en países distintos.
        entidad1 = EntidadExternaService.crear(
            nombre='Instituto Politécnico',
            sector='Educación',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        entidad2 = EntidadExternaService.crear(
            nombre='Instituto Politécnico',
            sector='Educación',
            pais='México',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        self.assertNotEqual(entidad1.pk, entidad2.pk)
        self.assertEqual(entidad1.nombre, entidad2.nombre)

    def test_actualizar_entidad_exitoso(self):
        entidad = EntidadExternaService.crear(
            nombre='Fundación Alfa',
            sector='ONG',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        actualizada = EntidadExternaService.actualizar(
            entidad_id=entidad.pk,
            ejecutor=self.ejecutor,
            sector='Fundación sin ánimo de lucro',
        )
        self.assertEqual(actualizada.sector, 'Fundación sin ánimo de lucro')
        self.assertEqual(actualizada.nombre, 'Fundación Alfa')  # no cambió

    def test_actualizar_entidad_tipo_relacion_invalido_falla(self):
        entidad = EntidadExternaService.crear(
            nombre='Fundación Beta',
            sector='ONG',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EntidadExternaService.actualizar(
                entidad_id=entidad.pk,
                ejecutor=self.ejecutor,
                tipo_relacion='INVALIDO',
            )

    def test_eliminar_entidad_sin_interacciones_exitoso(self):
        entidad = EntidadExternaService.crear(
            nombre='Fundación Gamma',
            sector='ONG',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        resultado = EntidadExternaService.eliminar(entidad.pk, ejecutor=self.ejecutor)
        self.assertTrue(resultado)
        self.assertFalse(
            EntidadExternaService.listar().filter(pk=entidad.pk).exists()
        )

    def test_eliminar_entidad_con_interacciones_falla(self):
        entidad = EntidadExternaService.crear(
            nombre='Fundación Delta',
            sector='ONG',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        InteraccionService.crear(
            entidad_id=entidad.pk,
            medio='REUNION',
            resumen='Primera reunión de acercamiento',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EntidadExternaService.eliminar(entidad.pk, ejecutor=self.ejecutor)
        # La entidad debe seguir existiendo
        self.assertTrue(
            EntidadExternaService.listar().filter(pk=entidad.pk).exists()
        )

    def test_listar_por_tipo_relacion(self):
        EntidadExternaService.crear(
            nombre='Empresa Financiadora',
            sector='Industria',
            pais='Colombia',
            tipo_relacion='FINANCIADOR',
            ejecutor=self.ejecutor,
        )
        EntidadExternaService.crear(
            nombre='ONG Cooperante',
            sector='ONG',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        financiadores = EntidadExternaService.listar_por_tipo_relacion('FINANCIADOR')
        self.assertEqual(financiadores.count(), 1)
        self.assertEqual(financiadores.first().nombre, 'Empresa Financiadora')

    def test_listar_por_pais(self):
        EntidadExternaService.crear(
            nombre='Entidad Colombiana',
            sector='Educación',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        EntidadExternaService.crear(
            nombre='Entidad Mexicana',
            sector='Educación',
            pais='México',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        colombianas = EntidadExternaService.listar_por_pais('Colombia')
        self.assertEqual(colombianas.count(), 1)
        self.assertEqual(colombianas.first().nombre, 'Entidad Colombiana')