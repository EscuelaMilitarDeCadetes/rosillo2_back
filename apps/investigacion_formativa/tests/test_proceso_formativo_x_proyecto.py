from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.usuarios.models import Usuario
from apps.institucional.models import Gerente
from apps.investigacion_formal.models import Proyecto
from apps.investigacion_formativa.services.proceso_formativo_x_proyecto_service import (
    ProcesoFormativoXProyectoService,
)


class ProcesoFormativoXProyectoServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        usuario_proyecto = Usuario.objects.create_user(
            username='investigador@esmic.edu.co',
            email='investigador@esmic.edu.co',
            password='investigador123',
        )
        gerente_persona = self._crear_persona(nombre='Luis', apellido='Torres', documento='555666777')
        gerente = Gerente.objects.create(persona=gerente_persona, estado=True)
        self.proyecto_formal = Proyecto.objects.create(
            usuario=usuario_proyecto, gerente=gerente, titulo='Proyecto formal de prueba',
            interno=True, registro_acta_cierre=False, alianza=False, estado=True,
            estado_aprobado='SIN_CALIFICAR', financiado=False, unidad_ejecutora='ING',
            linea_investigacion='Tecnología', codigo='', gruplac=False,
        )

    def _crear_vinculo(self):
        return ProcesoFormativoXProyectoService.crear(
            proceso_formativo_id=self.proceso.pk,
            proyecto_formal_id=self.proyecto_formal.pk,
            ejecutor=self.ejecutor,
        )

    def test_crear_vinculo_exitoso(self):
        vinculo = self._crear_vinculo()
        self.assertEqual(vinculo.proceso_formativo_id, self.proceso.pk)
        self.assertEqual(vinculo.proyecto_formal_id, self.proyecto_formal.pk)

    def test_crear_vinculo_duplicado_falla(self):
        self._crear_vinculo()
        with self.assertRaises(ValidationError):
            self._crear_vinculo()

    def test_crear_vinculo_proceso_inexistente_falla(self):
        with self.assertRaises(ValidationError):
            ProcesoFormativoXProyectoService.crear(
                proceso_formativo_id=999999,
                proyecto_formal_id=self.proyecto_formal.pk,
                ejecutor=self.ejecutor,
            )

    def test_actualizar_vinculo_exitoso(self):
        vinculo = self._crear_vinculo()
        otro_proceso = self.proceso  # mismo proceso, solo para probar el flujo de actualización
        actualizado = ProcesoFormativoXProyectoService.actualizar(
            vinculo_id=vinculo.pk,
            proceso_formativo_id=otro_proceso.pk,
            proyecto_formal_id=self.proyecto_formal.pk,
            ejecutor=self.ejecutor,
        )
        self.assertEqual(actualizado.pk, vinculo.pk)

    def test_eliminar_vinculo_soft_delete(self):
        vinculo = self._crear_vinculo()
        ProcesoFormativoXProyectoService.eliminar(vinculo.pk, ejecutor=self.ejecutor)
        vinculo.refresh_from_db()
        self.assertFalse(vinculo.activo)
        self.assertTrue(ProcesoFormativoXProyectoService.obtener(vinculo.pk).pk == vinculo.pk)

    def test_listar_por_proceso_formativo(self):
        self._crear_vinculo()
        resultado = ProcesoFormativoXProyectoService.listar_por_proceso_formativo(self.proceso.pk)
        self.assertEqual(resultado.count(), 1)