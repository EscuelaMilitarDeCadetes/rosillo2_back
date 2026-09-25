#apps/integracion/tests/test_permisos.py
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .base import IntegracionFixturesMixin


class PermisosVinculacionTests(IntegracionFixturesMixin, TestCase):

    def test_facultad_puede_crear_estudiante_jurado_tutor(self):
        self.crear_ejecutor_con_rol('FACULTAD', 'decano.facultad@esmic.edu.co')
        self.loguearse_como('decano.facultad@esmic.edu.co', 'soporte123', ambito='formativa')

        endpoints = {
            'crear-estudiante': 'ESTUDIANTE',
            'crear-jurado': 'JURADO',
            'crear-tutor': 'TUTOR',
        }

        for i, (url_name, nombre_rol) in enumerate(endpoints.items()):
            with self.subTest(rol=nombre_rol):
                data = self.datos_persona(
                    correo=f'{nombre_rol.lower()}.permiso@esmic.edu.co',
                    documento=f'PERM-{i}',
                )
                data['rol_plataforma_id'] = self.roles[nombre_rol].pk
                data['facultad_id'] = self.facultad.pk
                data['rol_grupo_id'] = self.rol_grupo.pk
                response = self.client.post(reverse(f'vinculacion-{url_name}'), data)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_facultad_no_puede_crear_soporte(self):
        self.crear_ejecutor_con_rol('FACULTAD', 'decano.facultad2@esmic.edu.co')
        self.loguearse_como('decano.facultad2@esmic.edu.co', 'soporte123')
        data = self.datos_persona(correo='intruso@esmic.edu.co', documento='INTRUSO-1')
        data['rol_plataforma_id'] = self.roles['SOPORTE'].pk
        response = self.client.post(reverse('vinculacion-crear-soporte'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_facultad_no_puede_crear_usuario_de_grupo(self):
        self.crear_ejecutor_con_rol('FACULTAD', 'decano.facultad3@esmic.edu.co')
        self.loguearse_como('decano.facultad3@esmic.edu.co', 'soporte123')
        data = self.datos_persona(correo='intruso2@esmic.edu.co', documento='INTRUSO-2')
        data['rol_plataforma_id'] = self.roles['GRUPO'].pk
        data['grupo_id'] = self.grupo.pk
        data['rol_grupo_id'] = self.rol_grupo.pk
        response = self.client.post(reverse('vinculacion-crear-grupo'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_sin_rol_no_puede_crear_nada(self):
        User = self.ejecutor.__class__
        User.objects.create_user(
            username='sinrol@esmic.edu.co', email='sinrol@esmic.edu.co',
            password='clave123', is_active=True,
        )
        self.intentar_login_debe_fallar('sinrol@esmic.edu.co', 'clave123')
        # Ya no se llega a crear nada: el usuario nunca obtuvo token.

    # ------------------------------------------------------------------ #
    # Regresión: hallazgo ronda 4/5 — /reemplazar/ sin permission_classes
    # permitía a cualquier usuario autenticado reasignar la Persona de
    # cualquier Usuario. Debe quedar restringido a SOPORTE.
    # ------------------------------------------------------------------ #
    def test_facultad_no_puede_reemplazar(self):
        self.crear_ejecutor_con_rol('FACULTAD', 'decano.reemplazo@esmic.edu.co')
        self.loguearse_como('decano.reemplazo@esmic.edu.co', 'soporte123')
        response = self.client.post(
            reverse('vinculacion-reemplazar'), {'usuario_id': self.ejecutor.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_sin_rol_no_puede_reemplazar(self):
        User = self.ejecutor.__class__
        User.objects.create_user(
            username='sinrol.reemplazo@esmic.edu.co', email='sinrol.reemplazo@esmic.edu.co',
            password='clave123', is_active=True,
        )
        self.intentar_login_debe_fallar('sinrol.reemplazo@esmic.edu.co', 'clave123')