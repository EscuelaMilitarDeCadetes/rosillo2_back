from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .base import CrmFixturesMixin
from apps.crm.services.entidad_externa_service import EntidadExternaService
from apps.crm.services.interaccion_service import InteraccionService


class InteraccionServiceTests(CrmFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.entidad = EntidadExternaService.crear(
            nombre='Entidad de Pruebas',
            sector='Educación',
            pais='Colombia',
            tipo_relacion='COOPERANTE',
            ejecutor=self.ejecutor,
        )
        self.proyecto = self._crear_proyecto('Proyecto de Interacciones')

    def test_crear_interaccion_exitoso_sin_proyecto_asociado(self):
        interaccion = InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Reunión inicial de acercamiento',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(interaccion.entidad_id, self.entidad.pk)
        self.assertIsNone(interaccion.proyecto_asociado_id)

    def test_crear_interaccion_con_proyecto_asociado_exitoso(self):
        interaccion = InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='CONVENIO',
            resumen='Firma de convenio marco',
            proyecto_asociado_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(interaccion.proyecto_asociado_id, self.proyecto.pk)

    def test_crear_interaccion_entidad_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            InteraccionService.crear(
                entidad_id=999999,
                medio='REUNION',
                resumen='Reunión con entidad inexistente',
                ejecutor=self.ejecutor,
            )

    def test_crear_interaccion_medio_invalido_falla(self):
        with self.assertRaises(ValidationError):
            InteraccionService.crear(
                entidad_id=self.entidad.pk,
                medio='LLAMADA',  # no es un valor válido
                resumen='Llamada de seguimiento',
                ejecutor=self.ejecutor,
            )

    def test_crear_interaccion_sin_resumen_falla(self):
        with self.assertRaises(ValidationError):
            InteraccionService.crear(
                entidad_id=self.entidad.pk,
                medio='REUNION',
                resumen='   ',
                ejecutor=self.ejecutor,
            )

    def test_crear_interaccion_proyecto_asociado_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            InteraccionService.crear(
                entidad_id=self.entidad.pk,
                medio='REUNION',
                resumen='Reunión con proyecto inválido',
                proyecto_asociado_id=999999,
                ejecutor=self.ejecutor,
            )

    def test_actualizar_interaccion_exitoso(self):
        interaccion = InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Resumen original',
            ejecutor=self.ejecutor,
        )
        actualizada = InteraccionService.actualizar(
            interaccion_id=interaccion.pk,
            ejecutor=self.ejecutor,
            resumen='Resumen corregido',
        )
        self.assertEqual(actualizada.resumen, 'Resumen corregido')
        self.assertEqual(actualizada.medio, 'REUNION')  # no cambió

    def test_actualizar_interaccion_asocia_proyecto_posteriormente(self):
        interaccion = InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Reunión sin proyecto aún',
            ejecutor=self.ejecutor,
        )
        actualizada = InteraccionService.actualizar(
            interaccion_id=interaccion.pk,
            ejecutor=self.ejecutor,
            proyecto_asociado_id=self.proyecto.pk,
        )
        self.assertEqual(actualizada.proyecto_asociado_id, self.proyecto.pk)

    def test_actualizar_interaccion_medio_invalido_falla(self):
        interaccion = InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Resumen original',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            InteraccionService.actualizar(
                interaccion_id=interaccion.pk,
                ejecutor=self.ejecutor,
                medio='INVALIDO',
            )

    def test_eliminar_interaccion_exitoso(self):
        interaccion = InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Interacción a eliminar',
            ejecutor=self.ejecutor,
        )
        resultado = InteraccionService.eliminar(interaccion.pk, ejecutor=self.ejecutor)
        self.assertTrue(resultado)
        self.assertFalse(
            InteraccionService.listar().filter(pk=interaccion.pk).exists()
        )

    def test_listar_por_entidad(self):
        otra_entidad = EntidadExternaService.crear(
            nombre='Otra Entidad',
            sector='Industria',
            pais='Colombia',
            tipo_relacion='FINANCIADOR',
            ejecutor=self.ejecutor,
        )
        InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Interacción entidad 1',
            ejecutor=self.ejecutor,
        )
        InteraccionService.crear(
            entidad_id=otra_entidad.pk,
            medio='REUNION',
            resumen='Interacción entidad 2',
            ejecutor=self.ejecutor,
        )
        interacciones = InteraccionService.listar_por_entidad(self.entidad.pk)
        self.assertEqual(interacciones.count(), 1)
        self.assertEqual(interacciones.first().resumen, 'Interacción entidad 1')

    def test_listar_por_proyecto(self):
        InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='CONVENIO',
            resumen='Interacción con proyecto',
            proyecto_asociado_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Interacción sin proyecto',
            ejecutor=self.ejecutor,
        )
        interacciones = InteraccionService.listar_por_proyecto(self.proyecto.pk)
        self.assertEqual(interacciones.count(), 1)
        self.assertEqual(interacciones.first().resumen, 'Interacción con proyecto')

    def test_listar_por_medio(self):
        InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='CONVENIO',
            resumen='Firma de convenio',
            ejecutor=self.ejecutor,
        )
        InteraccionService.crear(
            entidad_id=self.entidad.pk,
            medio='REUNION',
            resumen='Reunión de seguimiento',
            ejecutor=self.ejecutor,
        )
        convenios = InteraccionService.listar_por_medio('CONVENIO')
        self.assertEqual(convenios.count(), 1)
        self.assertEqual(convenios.first().resumen, 'Firma de convenio')