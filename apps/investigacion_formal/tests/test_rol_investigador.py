from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.rol_investigador_service import RolInvestigadorService


class RolInvestigadorServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def test_crear_rol_investigador_exitoso(self):
        rol = RolInvestigadorService.crear(
            nombre_rol_investigador='Investigador Principal',
            descripcion='Líder del proyecto de investigación',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(rol.nombre_rol_investigador, 'Investigador Principal')

    def test_crear_rol_investigador_nombre_duplicado_falla(self):
        RolInvestigadorService.crear(
            nombre_rol_investigador='Coinvestigador',
            descripcion='Apoyo al proyecto',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            RolInvestigadorService.crear(
                nombre_rol_investigador='coinvestigador',
                descripcion='Otro apoyo',
                ejecutor=self.ejecutor,
            )

    def test_crear_rol_investigador_sin_descripcion_falla(self):
        with self.assertRaises(ValidationError):
            RolInvestigadorService.crear(
                nombre_rol_investigador='Rol Sin Descripción',
                descripcion='   ',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_rol_investigador_exitoso(self):
        rol = RolInvestigadorService.crear(
            nombre_rol_investigador='Nombre Original',
            descripcion='Descripción original',
            ejecutor=self.ejecutor,
        )
        actualizado = RolInvestigadorService.actualizar(
            rol_investigador_id=rol.pk,
            nombre_rol_investigador='Nombre Corregido',
            descripcion='Descripción corregida',
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.nombre_rol_investigador, 'Nombre Corregido')

    def test_listar_roles_investigador(self):
        RolInvestigadorService.crear(
            nombre_rol_investigador='Rol 1', descripcion='Desc 1', ejecutor=self.ejecutor,
        )
        RolInvestigadorService.crear(
            nombre_rol_investigador='Rol 2', descripcion='Desc 2', ejecutor=self.ejecutor,
        )
        self.assertEqual(RolInvestigadorService.listar().count(), 2)