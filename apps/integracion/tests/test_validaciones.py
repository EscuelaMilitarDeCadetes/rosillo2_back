from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .base import IntegracionFixturesMixin


class ValidacionesVinculacionTests(IntegracionFixturesMixin, TestCase):

    def test_falta_documento_retorna_400(self):
        data = self.datos_persona(correo='sindoc@esmic.edu.co', documento='SD-1')
        data['rol_plataforma_id'] = self.roles['SOPORTE'].pk
        del data['documento']
        response = self.client.post(reverse('vinculacion-crear-soporte'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_falta_rol_plataforma_id_retorna_400(self):
        data = self.datos_persona(correo='sinrolplat@esmic.edu.co', documento='SRP-1')
        response = self.client.post(reverse('vinculacion-crear-soporte'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_flujo_facultad_sin_facultad_id_retorna_400(self):
        self.crear_ejecutor_con_rol('FACULTAD', 'validaciones.facultad@esmic.edu.co')
        self.loguearse_como('validaciones.facultad@esmic.edu.co', 'soporte123', ambito='formativa')
        data = self.datos_persona(correo='sinfac@esmic.edu.co', documento='SF-1')
        data['rol_plataforma_id'] = self.roles['ESTUDIANTE'].pk
        data['rol_grupo_id'] = self.rol_grupo.pk
        response = self.client.post(reverse('vinculacion-crear-estudiante'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_flujo_grupo_sin_grupo_id_retorna_400(self):
        data = self.datos_persona(correo='singru@esmic.edu.co', documento='SG-1')
        data['rol_plataforma_id'] = self.roles['GRUPO'].pk
        data['rol_grupo_id'] = self.rol_grupo.pk
        response = self.client.post(reverse('vinculacion-crear-grupo'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retirar_sin_usuario_id_retorna_400(self):
        response = self.client.post(reverse('vinculacion-retirar'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reemplazar_sin_usuario_id_retorna_400(self):
        response = self.client.post(reverse('vinculacion-reemplazar'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)