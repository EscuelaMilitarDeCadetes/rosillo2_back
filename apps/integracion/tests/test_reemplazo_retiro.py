from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from apps.usuarios.models import UsuarioXPersona
from apps.institucional.models import PersonaXGrupo
from .base import IntegracionFixturesMixin

User = get_user_model()


class ReemplazoRetiroTests(IntegracionFixturesMixin, TestCase):
    
    def setUp(self):
        super().setUp()
        self.crear_ejecutor_con_rol('FACULTAD', 'facultad.reemplazo@esmic.edu.co')
        self.loguearse_como('facultad.reemplazo@esmic.edu.co', 'soporte123', ambito='formativa')

    def _crear_estudiante_inicial(self, correo='original@esmic.edu.co', documento='ORIG-1'):
        data = self.datos_persona(correo=correo, documento=documento, nombre='Original')
        data['rol_plataforma_id'] = self.roles['ESTUDIANTE'].pk
        data['facultad_id'] = self.facultad.pk
        data['rol_grupo_id'] = self.rol_grupo.pk
        response = self.client.post(reverse('vinculacion-crear-estudiante'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['usuario']['id']

    def test_reemplazar_usuario_cierra_vinculo_anterior_y_crea_uno_nuevo(self):
        usuario_id = self._crear_estudiante_inicial()
        vinculo_anterior = PersonaXGrupo.objects.get(
            persona__correo='original@esmic.edu.co'
        )
        self.assertTrue(vinculo_anterior.estado)
        data_reemplazo = self.datos_persona(
            correo='reemplazo@esmic.edu.co', documento='REEMP-1', nombre='Reemplazo'
        )
        data_reemplazo['usuario_id'] = usuario_id
        data_reemplazo['rol_plataforma_id'] = self.roles['ESTUDIANTE'].pk
        data_reemplazo['facultad_id'] = self.facultad.pk
        data_reemplazo['rol_grupo_id'] = self.rol_grupo.pk
        self.loguearse_como('soporte@esmic.edu.co', 'soporte123')  # volver a SOPORTE
        response = self.client.post(reverse('vinculacion-reemplazar'), data_reemplazo)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vinculo_anterior.refresh_from_db()
        self.assertFalse(vinculo_anterior.estado)
        self.assertIsNotNone(vinculo_anterior.desvinculacion)
        self.assertTrue(
            PersonaXGrupo.objects.filter(
                persona__correo='reemplazo@esmic.edu.co',
                facultad=self.facultad,
                estado=True,
            ).exists()
        )
        self.assertTrue(
            UsuarioXPersona.objects.filter(
                usuario_id=usuario_id,
                persona__correo='reemplazo@esmic.edu.co',
                estado=True,
            ).exists()
        )
        self.assertFalse(
            UsuarioXPersona.objects.filter(
                usuario_id=usuario_id,
                persona__correo='original@esmic.edu.co',
                estado=True,
            ).exists()
        )

    def test_reemplazar_usuario_inactivo_falla(self):
        usuario_id = self._crear_estudiante_inicial(
            correo='inactivo@esmic.edu.co', documento='INACT-1'
        )
        User.objects.filter(pk=usuario_id).update(is_active=False)
        data_reemplazo = self.datos_persona(
            correo='nuevo@esmic.edu.co', documento='NUEVO-1'
        )
        data_reemplazo['usuario_id'] = usuario_id
        self.loguearse_como('soporte@esmic.edu.co', 'soporte123')   # <- línea agregada
        response = self.client.post(reverse('vinculacion-reemplazar'), data_reemplazo)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retirar_usuario_desactiva_usuario_y_vinculaciones(self):
        usuario_id = self._crear_estudiante_inicial(
            correo='retirar@esmic.edu.co', documento='RET-1'
        )
        response = self.client.post(
            reverse('vinculacion-retirar'), {'usuario_id': usuario_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usuario = User.objects.get(pk=usuario_id)
        self.assertFalse(usuario.is_active)
        vinculo = PersonaXGrupo.objects.get(persona__correo='retirar@esmic.edu.co')
        self.assertFalse(vinculo.estado)
        self.assertIsNotNone(vinculo.desvinculacion)

    def test_retirar_usuario_ya_inactivo_falla(self):
        usuario_id = self._crear_estudiante_inicial(
            correo='doble_retiro@esmic.edu.co', documento='DR-1'
        )
        self.client.post(reverse('vinculacion-retirar'), {'usuario_id': usuario_id})
        response = self.client.post(
            reverse('vinculacion-retirar'), {'usuario_id': usuario_id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)