from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from apps.usuarios.models import RolXUsuario
from apps.institucional.models import PersonaXGrupo
from apps.integracion.tests.base import IntegracionFixturesMixin


class AsignarRolExistenteTests(IntegracionFixturesMixin, TestCase):

    def _crear_usuario_sin_grupo(self):
        resp = self.client.post(reverse('vinculacion-crear-soporte'), {
            **self.datos_persona('nuevo@esmic.edu.co', '1000000001'),
            'rol_plataforma_id': self.roles['SOPORTE'].pk,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.data['usuario']['id']

    def test_asignar_rol_facultad_crea_personaxgrupo(self):
        usuario_id = self._crear_usuario_sin_grupo()
        resp = self.client.post(reverse('vinculacion-asignar-rol-existente'), {
            'usuario_id': usuario_id,
            'rol_plataforma_id': self.roles['FACULTAD'].pk,
            'facultad_id': self.facultad.pk,
            'rol_grupo_id': self.rol_grupo.pk,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data['vinculacion'])
        self.assertEqual(resp.data['vinculacion']['facultad_id'], self.facultad.pk)
        self.assertTrue(
            RolXUsuario.objects.filter(
                usuario_id=usuario_id, rol=self.roles['FACULTAD'], estado=True
            ).exists()
        )

    def test_asignar_rol_grupo_actualiza_vinculacion_existente(self):
        usuario_id = self._crear_usuario_sin_grupo()
        # primera asignación: FACULTAD
        self.client.post(reverse('vinculacion-asignar-rol-existente'), {
            'usuario_id': usuario_id,
            'rol_plataforma_id': self.roles['FACULTAD'].pk,
            'facultad_id': self.facultad.pk,
            'rol_grupo_id': self.rol_grupo.pk,
        })
        vinculaciones_antes = PersonaXGrupo.objects.count()
        # segunda asignación: mismo tipo (facultad), debe actualizar, no duplicar
        resp = self.client.post(reverse('vinculacion-asignar-rol-existente'), {
            'usuario_id': usuario_id,
            'rol_plataforma_id': self.roles['DECANO'].pk,
            'facultad_id': self.facultad.pk,
            'rol_grupo_id': self.rol_grupo.pk,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(PersonaXGrupo.objects.count(), vinculaciones_antes)

    def test_asignar_rol_sin_persona_falla(self):
        usuario = self.crear_ejecutor_con_rol('SOPORTE', 'huerfano@esmic.edu.co')
        resp = self.client.post(reverse('vinculacion-asignar-rol-existente'), {
            'usuario_id': usuario.pk,
            'rol_plataforma_id': self.roles['GRUPO'].pk,
            'grupo_id': self.grupo.pk,
            'rol_grupo_id': self.rol_grupo.pk,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asignar_rol_sin_componente_institucional_no_requiere_vinculo(self):
        usuario_id = self._crear_usuario_sin_grupo()
        resp = self.client.post(reverse('vinculacion-asignar-rol-existente'), {
            'usuario_id': usuario_id,
            'rol_plataforma_id': self.roles['SUPERVISOR'].pk,
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(resp.data.get('vinculacion'))