from datetime import date

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.models import GradoEstudios, Persona
from apps.institucional.services.gerente_service import GerenteService


class GerenteServiceTests(TestCase):
    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )
        grado = GradoEstudios.objects.create(sigla_grado='CIV', descripcion='Civil')
        self.persona1 = Persona.objects.create(
            grado=grado, nombre='Juan', apellido='Pérez',
            documento='111', celular='3001111111', correo='juan@esmic.edu.co',
        )
        self.persona2 = Persona.objects.create(
            grado=grado, nombre='Ana', apellido='Gómez',
            documento='222', celular='3002222222', correo='ana@esmic.edu.co',
        )

    def test_crear_primer_gerente_exitoso(self):
        gerente = GerenteService.crear(
            persona_id=self.persona1.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 1, 1),
        )
        self.assertTrue(gerente.estado)
        self.assertIsNone(gerente.fecha_salida)

    def test_crear_nuevo_gerente_cierra_al_anterior_automaticamente(self):
        gerente1 = GerenteService.crear(
            persona_id=self.persona1.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 1, 1),
        )
        gerente2 = GerenteService.crear(
            persona_id=self.persona2.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 6, 1),
        )
        gerente1.refresh_from_db()
        self.assertFalse(gerente1.estado)
        self.assertEqual(gerente1.fecha_salida, date(2024, 6, 1))
        self.assertTrue(gerente2.estado)

    def test_crear_gerente_sin_persona_falla(self):
        with self.assertRaises(ValidationError):
            GerenteService.crear(persona_id=None, ejecutor=self.ejecutor)

    def test_crear_gerente_persona_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            GerenteService.crear(persona_id=99999, ejecutor=self.ejecutor)

    def test_obtener_actual(self):
        GerenteService.crear(
            persona_id=self.persona1.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 1, 1),
        )
        actual = GerenteService.obtener_actual()
        self.assertEqual(actual.persona, self.persona1)

    def test_finalizar_gerente(self):
        gerente = GerenteService.crear(
            persona_id=self.persona1.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 1, 1),
        )
        finalizado = GerenteService.finalizar(
            gerente.pk, ejecutor=self.ejecutor, fecha_salida=date(2024, 12, 31)
        )
        self.assertFalse(finalizado.estado)
        self.assertEqual(finalizado.fecha_salida, date(2024, 12, 31))
        self.assertIsNone(GerenteService.obtener_actual())

    def test_actualizar_fecha_salida_anterior_a_ingreso_falla(self):
        gerente = GerenteService.crear(
            persona_id=self.persona1.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 6, 1),
        )
        with self.assertRaises(ValidationError):
            GerenteService.actualizar(
                gerente.pk,
                ejecutor=self.ejecutor,
                fecha_salida=date(2024, 1, 1),  # anterior al ingreso
            )

    def test_actualizar_reactivar_gerente_cuando_hay_otro_activo_falla(self):
        gerente1 = GerenteService.crear(
            persona_id=self.persona1.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 1, 1),
        )
        # gerente2 reemplaza y cierra a gerente1 automáticamente
        GerenteService.crear(
            persona_id=self.persona2.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 6, 1),
        )
        # Intentar reactivar gerente1 (quitarle fecha_salida) debe fallar
        # porque ya hay un gerente activo (gerente2).
        with self.assertRaises(ValidationError):
            GerenteService.actualizar(
                gerente1.pk,
                ejecutor=self.ejecutor,
                fecha_salida=None,
            )

    def test_eliminar_gerente_soft_delete(self):
        gerente = GerenteService.crear(
            persona_id=self.persona1.pk,
            ejecutor=self.ejecutor,
            fecha_ingreso=date(2024, 1, 1),
        )
        GerenteService.eliminar(gerente.pk, ejecutor=self.ejecutor)
        gerente.refresh_from_db()
        self.assertFalse(gerente.estado)