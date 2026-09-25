# apps/integracion/tests/base.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import RolPlataforma, RolXUsuario
from apps.institucional.models import (
    GradoEstudios, FacultadEscuela, GrupoInvestigacion, RolGrupo, FacultadXGrupo,
)
from django.core.cache import cache

User = get_user_model()


class IntegracionFixturesMixin:
    """
    Cataloga lo mínimo indispensable (roles de plataforma, grado,
    facultad, grupo, FacultadXGrupo) y deja logueado por defecto un
    ejecutor con rol SOPORTE, listo para pegarle a los endpoints de
    VinculacionViewSet.

    Solo va aquí lo que TODAS las clases de test de este módulo
    necesitan. Fixtures propios de un único archivo (por ejemplo
    persona/usuario/asignacion de test_ciclo_vida_usuario.py) van en el
    setUp() de esa clase específica, no aquí — para no inflar el fixture
    compartido con cosas que la mayoría de las pruebas no usa.
    """

    ROLES_NOMBRES = [
        'SOPORTE', 'SUPERVISOR', 'GERENTE',
        'DECANO', 'FACULTAD', 'ESTUDIANTE', 'JURADO', 'TUTOR',
        'GRUPO', 'CINTERNO', 'CEXTERNO', 'ASESOR',
    ]

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.roles = {
            nombre: RolPlataforma.objects.create(
                nombre_rol=nombre, descripcion=f'Rol {nombre}'
            )
            for nombre in self.ROLES_NOMBRES
        }
        self.grado = GradoEstudios.objects.create(
            sigla_grado='CIV', descripcion='Civil'
        )
        self.facultad = FacultadEscuela.objects.create(
            nombre_facultad='Facultad de Ingeniería', abreviatura='ING'
        )
        self.grupo = GrupoInvestigacion.objects.create(
            nombre_grupo='Grupo de Pruebas', sigla_grupo='GP'
        )
        FacultadXGrupo.objects.create(grupo=self.grupo, facultad=self.facultad)
        self.rol_grupo = RolGrupo.objects.create(cargo='Investigador')
        self.ejecutor = self.crear_ejecutor_con_rol('SOPORTE', 'soporte@esmic.edu.co')
        self.loguearse_como('soporte@esmic.edu.co', 'soporte123')

    def crear_ejecutor_con_rol(self, nombre_rol, username, password='soporte123'):
        usuario = User.objects.create_user(
            username=username, email=username, password=password, is_active=True
        )
        RolXUsuario.objects.create(
            usuario=usuario, rol=self.roles[nombre_rol], estado=True
        )
        return usuario

    def loguearse_como(self, username, password, ambito='formal'):
        """
        Autentica al usuario en el ámbito indicado y configura el JWT
        correspondiente en el cliente de pruebas.

        Valores permitidos:
            - 'formal'
            - 'formativa'
        """
        if ambito == 'formal':
            login_url = reverse('login-formal')
        elif ambito == 'formativa':
            login_url = reverse('login-formativa')
        else:
            raise ValueError(
                f"Ámbito inválido: '{ambito}'. "
                "Los valores permitidos son 'formal' y 'formativa'."
            )
        login = self.client.post(login_url,{'username': username,'password': password,},)
        self.assertEqual(login.status_code,status.HTTP_200_OK,msg=(
                f"No fue posible autenticar '{username}' "
                f"en el ámbito '{ambito}'. "
                f"Respuesta: {getattr(login, 'data', login.content)}"
            ))
        self.assertEqual(login.data.get('ambito'),ambito,msg=(
                f"El login de '{username}' no devolvió el ámbito esperado. "
                f"Esperado: '{ambito}'. "
                f"Recibido: '{login.data.get('ambito')}'."
            ))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        return login.data

    def intentar_login_debe_fallar(self, username, password):
        login = self.client.post(reverse('login-formal'), {
            'username': username, 'password': password,
        })
        self.assertEqual(login.status_code, status.HTTP_403_FORBIDDEN)

    def datos_persona(self, correo, documento, nombre='Nombre', apellido='Apellido', celular=None):
        return {
            'grado_id': self.grado.pk,
            'nombre': nombre,
            'apellido': apellido,
            'documento': documento,
            'celular': celular or f'30{documento[-8:].zfill(8)}',
            'correo': correo,
            'username': correo,
            'password': 'Temporal123!',
        }