from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from apps.usuarios.models import UsuarioXPersona, RolXUsuario
from apps.institucional.models import PersonaXGrupo
from .base import IntegracionFixturesMixin

ENDPOINTS_QUE_REQUIEREN_FACULTAD = {'crear-estudiante', 'crear-jurado', 'crear-tutor'}


class FlujoAdministrativoTests(IntegracionFixturesMixin, TestCase):
    """SOPORTE, SUPERVISOR, GERENTE: Persona + Usuario + RolXUsuario,
    SIN PersonaXGrupo."""

    ENDPOINTS_POR_ROL = {
        'crear-soporte': 'SOPORTE',
        'crear-supervisor': 'SUPERVISOR',
        'crear-gerente': 'GERENTE',
    }

    def test_crea_persona_usuario_y_rol_sin_vinculacion_institucional(self):
        for i, (url_name, nombre_rol) in enumerate(self.ENDPOINTS_POR_ROL.items()):
            with self.subTest(rol=nombre_rol):
                data = self.datos_persona(
                    correo=f'nuevo.{nombre_rol.lower()}@esmic.edu.co',   
                    documento=f'ADM-{i}',
                )
                data['rol_plataforma_id'] = self.roles[nombre_rol].pk
                response = self.client.post(reverse(f'vinculacion-{url_name}'), data)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                usuario_id = response.data['usuario']['id']
                self.assertTrue(
                    UsuarioXPersona.objects.filter(
                        usuario_id=usuario_id, estado=True
                    ).exists()
                )
                self.assertTrue(
                    RolXUsuario.objects.filter(
                        usuario_id=usuario_id,
                        rol__nombre_rol=nombre_rol,
                        estado=True,
                    ).exists()
                )
                self.assertFalse(
                    PersonaXGrupo.objects.filter(
                        persona__correo=data['correo']
                    ).exists()
                )


class FlujoFacultadTests(IntegracionFixturesMixin, TestCase):
    """DECANO, FACULTAD, ESTUDIANTE, JURADO, TUTOR: + PersonaXGrupo
    con facultad, sin grupo."""

    ENDPOINTS_QUE_REQUIEREN_FACULTAD = {'crear-estudiante', 'crear-jurado', 'crear-tutor'}  

    ENDPOINTS_POR_ROL = {
        'crear-decano': 'DECANO',
        'crear-facultad': 'FACULTAD',
        'crear-estudiante': 'ESTUDIANTE',
        'crear-jurado': 'JURADO',
        'crear-tutor': 'TUTOR',
    }

    def test_crea_vinculacion_con_facultad_y_sin_grupo(self):
        for i, (url_name, nombre_rol) in enumerate(self.ENDPOINTS_POR_ROL.items()):
            with self.subTest(rol=nombre_rol):
                if url_name in self.ENDPOINTS_QUE_REQUIEREN_FACULTAD:
                    self.crear_ejecutor_con_rol(
                        'FACULTAD', f'coordinador{i}.facultad@esmic.edu.co'
                    )
                    self.loguearse_como(f'coordinador{i}.facultad@esmic.edu.co', 'soporte123', ambito='formativa')
                else:
                    self.loguearse_como('soporte@esmic.edu.co', 'soporte123')
                data = self.datos_persona(
                    correo=f'{nombre_rol.lower()}@esmic.edu.co',
                    documento=f'FAC-{i}',
                )
                data['rol_plataforma_id'] = self.roles[nombre_rol].pk
                data['facultad_id'] = self.facultad.pk
                data['rol_grupo_id'] = self.rol_grupo.pk
                response = self.client.post(reverse(f'vinculacion-{url_name}'), data)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FlujoGrupoTests(IntegracionFixturesMixin, TestCase):
    """GRUPO, CINTERNO, CEXTERNO, ASESOR: + PersonaXGrupo con grupo,
    sin facultad."""

    ENDPOINTS_POR_ROL = {
        'crear-grupo': 'GRUPO',
        'crear-cinterno': 'CINTERNO',
        'crear-cexterno': 'CEXTERNO',
        'crear-asesor': 'ASESOR',
    }

    def test_crea_vinculacion_con_grupo_y_sin_facultad(self):
        for i, (url_name, nombre_rol) in enumerate(self.ENDPOINTS_POR_ROL.items()):
            with self.subTest(rol=nombre_rol):
                data = self.datos_persona(
                    correo=f'{nombre_rol.lower()}@esmic.edu.co',
                    documento=f'GRP-{i}',
                )
                data['rol_plataforma_id'] = self.roles[nombre_rol].pk
                data['grupo_id'] = self.grupo.pk
                data['rol_grupo_id'] = self.rol_grupo.pk
                response = self.client.post(reverse(f'vinculacion-{url_name}'), data)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                vinculacion = PersonaXGrupo.objects.get(
                    persona__correo=data['correo']
                )
                self.assertEqual(vinculacion.grupo_id, self.grupo.pk)
                self.assertIsNone(vinculacion.facultad_id)