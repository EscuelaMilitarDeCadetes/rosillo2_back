from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.investigador_x_proyecto_service import (
    InvestigadorXProyectoService,
)


class InvestigadorXProyectoServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proyecto = self._crear_proyecto()
        self.rol_investigador = self._crear_rol_investigador()

    def test_crear_investigador_x_proyecto_exitoso(self):
        investigador = InvestigadorXProyectoService.crear(
            rol_investigador_id=self.rol_investigador.pk,
            proyecto_id=self.proyecto.pk,
            persona_x_grupo_id=self.persona_x_grupo.pk,
            ejecutor=self.ejecutor,
        )
        self.assertTrue(investigador.estado)

    def test_crear_investigador_x_proyecto_duplicado_falla(self):
        InvestigadorXProyectoService.crear(
            rol_investigador_id=self.rol_investigador.pk,
            proyecto_id=self.proyecto.pk,
            persona_x_grupo_id=self.persona_x_grupo.pk,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            InvestigadorXProyectoService.crear(
                rol_investigador_id=self.rol_investigador.pk,
                proyecto_id=self.proyecto.pk,
                persona_x_grupo_id=self.persona_x_grupo.pk,
                ejecutor=self.ejecutor,
            )

    def test_crear_investigador_x_proyecto_sin_rol_falla(self):
        with self.assertRaises(ValidationError):
            InvestigadorXProyectoService.crear(
                rol_investigador_id=None,
                proyecto_id=self.proyecto.pk,
                persona_x_grupo_id=self.persona_x_grupo.pk,
                ejecutor=self.ejecutor,
            )

    def test_actualizar_investigador_x_proyecto_exitoso(self):
        investigador = InvestigadorXProyectoService.crear(
            rol_investigador_id=self.rol_investigador.pk,
            proyecto_id=self.proyecto.pk,
            persona_x_grupo_id=self.persona_x_grupo.pk,
            ejecutor=self.ejecutor,
        )
        otro_rol = self._crear_rol_investigador(nombre='Coinvestigador')
        actualizado = InvestigadorXProyectoService.actualizar(
            investigador_x_proyecto_id=investigador.pk,
            ejecutor=self.ejecutor,
            rol_investigador_id=otro_rol.pk,
        )
        self.assertEqual(actualizado.rol_investigador_id, otro_rol.pk)

    def test_eliminar_investigador_x_proyecto_soft_delete(self):
        investigador = InvestigadorXProyectoService.crear(
            rol_investigador_id=self.rol_investigador.pk,
            proyecto_id=self.proyecto.pk,
            persona_x_grupo_id=self.persona_x_grupo.pk,
            ejecutor=self.ejecutor,
        )
        InvestigadorXProyectoService.eliminar(investigador.pk, ejecutor=self.ejecutor)
        investigador.refresh_from_db()
        self.assertFalse(investigador.estado)

    def test_eliminar_investigador_x_proyecto_ya_retirado_falla(self):
        investigador = InvestigadorXProyectoService.crear(
            rol_investigador_id=self.rol_investigador.pk,
            proyecto_id=self.proyecto.pk,
            persona_x_grupo_id=self.persona_x_grupo.pk,
            ejecutor=self.ejecutor,
        )
        InvestigadorXProyectoService.eliminar(investigador.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            InvestigadorXProyectoService.eliminar(investigador.pk, ejecutor=self.ejecutor)

    def test_listar_por_proyecto_solo_activos(self):
        investigador = InvestigadorXProyectoService.crear(
            rol_investigador_id=self.rol_investigador.pk,
            proyecto_id=self.proyecto.pk,
            persona_x_grupo_id=self.persona_x_grupo.pk,
            ejecutor=self.ejecutor,
        )
        InvestigadorXProyectoService.eliminar(investigador.pk, ejecutor=self.ejecutor)
        resultado = InvestigadorXProyectoService.listar_por_proyecto(
            self.proyecto.pk, solo_activos=True
        )
        self.assertEqual(resultado.count(), 0)