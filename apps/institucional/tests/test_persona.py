from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.usuarios.models import Usuario
from apps.institucional.models import GradoEstudios
from apps.institucional.services.persona_service import PersonaService
from apps.institucional.validators.persona_validator import PersonaValidator


class PersonaServiceTests(TestCase):
    def setUp(self):
        self.ejecutor = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='admin123',
        )
        self.grado = GradoEstudios.objects.create(
            sigla_grado='CIV', descripcion='Civil'
        )

    def test_crear_persona_exitoso(self):
        persona = PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Juan',
            apellido='Pérez',
            documento='123456789',
            celular='3001234567',
            correo='juan.perez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(persona.nombre, 'Juan')
        self.assertEqual(persona.correo, 'juan.perez@esmic.edu.co')

    def test_crear_persona_documento_duplicado_falla(self):
        PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Juan',
            apellido='Pérez',
            documento='123456789',
            celular='3001234567',
            correo='juan.perez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            PersonaService.crear(
                grado_id=self.grado.pk,
                nombre='Otro',
                apellido='Nombre',
                documento='123456789',
                celular='3009999999',
                correo='otro@esmic.edu.co',
                ejecutor=self.ejecutor,
            )

    def test_crear_persona_correo_duplicado_falla(self):
        PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Juan',
            apellido='Pérez',
            documento='123456789',
            celular='3001234567',
            correo='juan.perez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            PersonaService.crear(
                grado_id=self.grado.pk,
                nombre='Otro',
                apellido='Nombre',
                documento='987654321',
                celular='3009999999',
                correo='juan.perez@esmic.edu.co',
                ejecutor=self.ejecutor,
            )

    def test_crear_persona_celular_duplicado_falla(self):
        PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Juan',
            apellido='Pérez',
            documento='123456789',
            celular='3001234567',
            correo='juan.perez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            PersonaService.crear(
                grado_id=self.grado.pk,
                nombre='Otro',
                apellido='Nombre',
                documento='987654321',
                celular='3001234567',  # mismo celular
                correo='otro@esmic.edu.co',
                ejecutor=self.ejecutor,
            )

    def test_crear_persona_grado_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            PersonaService.crear(
                grado_id=99999,
                nombre='Juan',
                apellido='Pérez',
                documento='123456789',
                celular='3001234567',
                correo='juan.perez@esmic.edu.co',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_persona_exitoso(self):
        persona = PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Juan',
            apellido='Pérez',
            documento='123456789',
            celular='3001234567',
            correo='juan.perez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        actualizada = PersonaService.actualizar(
            persona_id=persona.pk,
            ejecutor=self.ejecutor,
            nombre='Juan Carlos',
        )
        self.assertEqual(actualizada.nombre, 'Juan Carlos')
        self.assertEqual(actualizada.apellido, 'Pérez')  # no se tocó

    def test_actualizar_persona_documento_duplicado_con_otro_falla(self):
        PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Juan',
            apellido='Pérez',
            documento='123456789',
            celular='3001234567',
            correo='juan.perez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        persona2 = PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Ana',
            apellido='Gómez',
            documento='987654321',
            celular='3009999999',
            correo='ana.gomez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            PersonaService.actualizar(
                persona_id=persona2.pk,
                ejecutor=self.ejecutor,
                documento='123456789',  # documento de la otra persona
            )

    def test_actualizar_persona_mismo_documento_no_falla(self):
        # Excluir el propio id de la validación de unicidad
        persona = PersonaService.crear(
            grado_id=self.grado.pk,
            nombre='Juan',
            apellido='Pérez',
            documento='123456789',
            celular='3001234567',
            correo='juan.perez@esmic.edu.co',
            ejecutor=self.ejecutor,
        )
        actualizada = PersonaService.actualizar(
            persona_id=persona.pk,
            ejecutor=self.ejecutor,
            documento='123456789',
            apellido='Pérez Actualizado',
        )
        self.assertEqual(actualizada.apellido, 'Pérez Actualizado')


class PersonaValidatorTests(TestCase):
    def setUp(self):
        self.grado = GradoEstudios.objects.create(
            sigla_grado='MAG', descripcion='Magister'
        )

    def test_validar_creacion_correo_sin_arroba_falla(self):
        with self.assertRaises(ValidationError):
            PersonaValidator.validar_creacion(
                grado_id=self.grado.pk,
                nombre='Juan',
                apellido='Pérez',
                documento='123456789',
                celular='3001234567',
                correo='correo-invalido',
            )

    def test_validar_creacion_nombre_vacio_falla(self):
        with self.assertRaises(ValidationError):
            PersonaValidator.validar_creacion(
                grado_id=self.grado.pk,
                nombre='   ',
                apellido='Pérez',
                documento='123456789',
                celular='3001234567',
                correo='juan@esmic.edu.co',
            )

    def test_validar_creacion_grado_nulo_falla(self):
        with self.assertRaises(ValidationError):
            PersonaValidator.validar_creacion(
                grado_id=None,
                nombre='Juan',
                apellido='Pérez',
                documento='123456789',
                celular='3001234567',
                correo='juan@esmic.edu.co',
            )