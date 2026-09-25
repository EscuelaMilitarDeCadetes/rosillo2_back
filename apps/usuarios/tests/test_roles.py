#apps/usuarios/tests/test_roles.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError
from datetime import date
from apps.usuarios.models import Usuario, RolPlataforma, RolXUsuario, UsuarioXPersona
from apps.usuarios.services.rol_x_usuario_service import RolXUsuarioService
from apps.institucional.models import (
    Persona, GradoEstudios, FacultadEscuela, RolGrupo, PersonaXGrupo,
)


class RolXUsuarioTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.rol_soporte = RolPlataforma.objects.create(
            nombre_rol='SOPORTE',
            descripcion='Gestiona usuarios'
        )
        self.rol_supervisor = RolPlataforma.objects.create(
            nombre_rol='SUPERVISOR',
            descripcion='Solo lectura'
        )
        self.admin = Usuario.objects.create_user(
            username='admin@esmic.edu.co',
            email='admin@esmic.edu.co',
            password='Admin123*',
            is_active=True
        )
        RolXUsuario.objects.create(
            usuario=self.admin,
            rol=self.rol_soporte,
            estado=True
        )
        self.target_user = Usuario.objects.create_user(
            username='target@esmic.edu.co',
            email='target@esmic.edu.co',
            password='Target123*',
            is_active=True
        )
        login = self.client.post(reverse('login-formal'), {
            'username': 'admin@esmic.edu.co',
            'password': 'Admin123*'
        })
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )

    def test_delete_no_permitido_sobre_rol_plataforma(self):
        """
        RolPlataformaViewSet es un catálogo (viewsets.ViewSet puro):
        no define destroy(), por lo tanto DELETE debe responder 405.
        Los catálogos son permanentes, sin endpoint de borrado (11_backend_logic.md).
        """
        response = self.client.delete(f'/api/usuarios/roles/{self.rol_soporte.id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_agregar_rol(self):
        response = self.client.post(
            '/api/usuarios/roles-usuario/agregar-rol/',
            {
                'usuario_id': self.target_user.id,
                'rol_id': self.rol_supervisor.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            RolXUsuario.objects.filter(
                usuario=self.target_user,
                rol=self.rol_supervisor,
                estado=True
            ).exists()
        )

    def test_borrar_rol(self):
        RolXUsuario.objects.create(
            usuario=self.target_user,
            rol=self.rol_supervisor,
            estado=True
        )
        response = self.client.post(
            '/api/usuarios/roles-usuario/borrar-rol/',
            {
                'usuario_id': self.target_user.id,
                'rol_id': self.rol_supervisor.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            RolXUsuario.objects.filter(
                usuario=self.target_user,
                rol=self.rol_supervisor,
                estado=True
            ).exists()
        )

    def test_usuario_sin_rol_no_puede_acceder(self):
        Usuario.objects.create_user(
            username='sinrol@esmic.edu.co',
            email='sinrol@esmic.edu.co',
            password='Sinrol123*',
            is_active=True
        )
        login = self.client.post(reverse('login-formal'), {
            'username': 'sinrol@esmic.edu.co',
            'password': 'Sinrol123*'
        })
        self.assertEqual(login.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_put_no_permitido_sobre_rol_x_usuario(self):
        rxu = RolXUsuario.objects.create(usuario=self.target_user, rol=self.rol_supervisor, estado=True)
        response = self.client.put(f'/api/usuarios/roles-usuario/{rxu.id}/', {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_no_permitido_sobre_rol_plataforma(self):
        response = self.client.put(
            f'/api/usuarios/roles/{self.rol_soporte.id}/',
            {'nombre_rol': 'MODIFICADO'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_historico_incluye_roles_inactivos(self):
        rxu = RolXUsuario.objects.create(usuario=self.target_user, rol=self.rol_supervisor, estado=True)
        rxu.estado = False
        rxu.save(update_fields=['estado'])
        response = self.client.get(f'/api/usuarios/roles-usuario/historico/{self.target_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(not r['estado'] for r in response.data))
        
    def test_soporte_puede_editar_un_rol_de_plataforma(self):
        rol = RolPlataforma.objects.create(nombre_rol="TEMP", descripcion="temporal")
        self.client.force_authenticate(user=self.admin)   
        response = self.client.patch(
            f"/api/usuarios/roles/{rol.id}/",
            {"descripcion": "descripcion actualizada"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        rol.refresh_from_db()
        self.assertEqual(rol.descripcion, "descripcion actualizada")
        
    
class RolXUsuarioServiceGuardTests(TestCase):
    """
    RolXUsuarioService.agregar_rol_a_usuario() debe rechazar la 
    asignación directa de un rol con vínculo institucional
    (FACULTAD/GRUPO) si el usuario no tiene ya un PersonaXGrupo activo. El
    único camino soportado para ese caso es
    VinculacionService.asignar_rol_existente().
    """

    def setUp(self):
        self.rol_facultad = RolPlataforma.objects.create(
            nombre_rol='FACULTAD', descripcion='Requiere vínculo de facultad'
        )
        self.rol_soporte = RolPlataforma.objects.create(
            nombre_rol='SOPORTE', descripcion='No requiere vínculo'
        )
        self.admin = Usuario.objects.create_user(
            username='admin_guard@esmic.edu.co',
            email='admin_guard@esmic.edu.co',
            password='Admin123*',
            is_active=True,
        )

    # ------------------------------------------------------------------ #
    # Caso 1: rol con vínculo + usuario SIN PersonaXGrupo activo -> falla
    # ------------------------------------------------------------------ #
    def test_agregar_rol_facultad_sin_vinculo_activo_lanza_validation_error(self):
        usuario_sin_vinculo = Usuario.objects.create_user(
            username='sinvinculo@esmic.edu.co',
            email='sinvinculo@esmic.edu.co',
            password='Sin123*',
            is_active=True,
        )
        with self.assertRaises(ValidationError):
            RolXUsuarioService.agregar_rol_a_usuario(
                usuario_id=usuario_sin_vinculo.id,
                rol_id=self.rol_facultad.id,
                ejecutor=self.admin,
            )
        # No debe haber creado el RolXUsuario: la transacción se revierte.
        self.assertFalse(
            RolXUsuario.objects.filter(
                usuario=usuario_sin_vinculo, rol=self.rol_facultad
            ).exists()
        )

    # ------------------------------------------------------------------ #
    # Caso 2: rol con vínculo + usuario CON PersonaXGrupo activo -> funciona
    # ------------------------------------------------------------------ #
    def test_agregar_rol_facultad_con_vinculo_activo_funciona(self):
        grado = GradoEstudios.objects.create(sigla_grado='CIV', descripcion='Civil')
        persona = Persona.objects.create(
            grado=grado,
            nombre='Persona',
            apellido='Con Vinculo',
            documento='900000099',
            celular='3000000099',
            correo='convinculo@esmic.edu.co',
        )
        usuario_con_vinculo = Usuario.objects.create_user(
            username='convinculo@esmic.edu.co',
            email='convinculo@esmic.edu.co',
            password='Con123*',
            is_active=True,
        )
        UsuarioXPersona.objects.create(
            usuario=usuario_con_vinculo, persona=persona, estado=True
        )
        facultad = FacultadEscuela.objects.create(
            nombre_facultad='Facultad de Prueba', abreviatura='FP'
        )
        rol_grupo = RolGrupo.objects.create(cargo='Decano')
        PersonaXGrupo.objects.create(
            persona=persona,
            rol_grupo=rol_grupo,
            facultad=facultad,
            vinculacion=date.today(),
            estado=True,
        )
        rxu = RolXUsuarioService.agregar_rol_a_usuario(
            usuario_id=usuario_con_vinculo.id,
            rol_id=self.rol_facultad.id,
            ejecutor=self.admin,
        )
        self.assertTrue(rxu.estado)
        self.assertTrue(
            RolXUsuario.objects.filter(
                usuario=usuario_con_vinculo, rol=self.rol_facultad, estado=True
            ).exists()
        )

    # ------------------------------------------------------------------ #
    # Caso 3: rol SIN vínculo -> el guard ni se activa, comportamiento igual
    # ------------------------------------------------------------------ #
    def test_agregar_rol_sin_vinculo_no_requiere_persona(self):
        usuario_sin_persona = Usuario.objects.create_user(
            username='sinpersona@esmic.edu.co',
            email='sinpersona@esmic.edu.co',
            password='Sin123*',
            is_active=True,
        )
        # Deliberadamente sin Persona/UsuarioXPersona: SOPORTE no lo necesita.
        rxu = RolXUsuarioService.agregar_rol_a_usuario(
            usuario_id=usuario_sin_persona.id,
            rol_id=self.rol_soporte.id,
            ejecutor=self.admin,
        )
        self.assertTrue(rxu.estado)
        self.assertTrue(
            RolXUsuario.objects.filter(
                usuario=usuario_sin_persona, rol=self.rol_soporte, estado=True
            ).exists()
        )