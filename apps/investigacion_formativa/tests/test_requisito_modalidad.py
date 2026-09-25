from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormativaFixturesMixin
from apps.investigacion_formativa.services.requisito_modalidad_service import (
    RequisitoModalidadService,
)


class RequisitoModalidadServiceTests(InvestigacionFormativaFixturesMixin, TestCase):

    def test_crear_requisito_numerico_exitoso(self):
        requisito = RequisitoModalidadService.crear(
            modalidad_id=self.modalidad.pk,
            tipo='HORAS_MINIMAS',
            descripcion='Mínimo de horas exigidas',
            ejecutor=self.ejecutor,
            valor_numerico=120,
        )
        self.assertEqual(requisito.valor_numerico, 120)
        self.assertTrue(requisito.activo)

    def test_crear_requisito_booleano_exitoso(self):
        requisito = RequisitoModalidadService.crear(
            modalidad_id=self.modalidad.pk,
            tipo='PROYECTO_FORMAL',
            descripcion='Debe estar vinculado a un proyecto formal',
            ejecutor=self.ejecutor,
            valor_booleano=True,
        )
        self.assertTrue(requisito.valor_booleano)

    def test_crear_requisito_numerico_sin_valor_falla(self):
        with self.assertRaises(ValidationError):
            RequisitoModalidadService.crear(
                modalidad_id=self.modalidad.pk,
                tipo='HORAS_MINIMAS',
                descripcion='Mínimo de horas exigidas',
                ejecutor=self.ejecutor,
            )

    def test_crear_requisito_booleano_sin_valor_falla(self):
        with self.assertRaises(ValidationError):
            RequisitoModalidadService.crear(
                modalidad_id=self.modalidad.pk,
                tipo='PROYECTO_FORMAL',
                descripcion='Debe estar vinculado a un proyecto formal',
                ejecutor=self.ejecutor,
            )

    def test_crear_requisito_duplicado_para_mismo_tipo_falla(self):
        RequisitoModalidadService.crear(
            modalidad_id=self.modalidad.pk, tipo='HORAS_MINIMAS',
            descripcion='Descripción', ejecutor=self.ejecutor, valor_numerico=120,
        )
        with self.assertRaises(ValidationError):
            RequisitoModalidadService.crear(
                modalidad_id=self.modalidad.pk, tipo='HORAS_MINIMAS',
                descripcion='Otra descripción', ejecutor=self.ejecutor, valor_numerico=100,
            )

    def test_actualizar_requisito_exitoso(self):
        requisito = RequisitoModalidadService.crear(
            modalidad_id=self.modalidad.pk, tipo='HORAS_MINIMAS',
            descripcion='Descripción', ejecutor=self.ejecutor, valor_numerico=120,
        )
        actualizado = RequisitoModalidadService.actualizar(
            requisito_id=requisito.pk, tipo='HORAS_MINIMAS',
            descripcion='Descripción actualizada', ejecutor=self.ejecutor, valor_numerico=100,
        )
        self.assertEqual(actualizado.valor_numerico, 100)

    def test_eliminar_requisito_soft_delete(self):
        requisito = RequisitoModalidadService.crear(
            modalidad_id=self.modalidad.pk, tipo='HORAS_MINIMAS',
            descripcion='Descripción', ejecutor=self.ejecutor, valor_numerico=120,
        )
        RequisitoModalidadService.eliminar(requisito.pk, ejecutor=self.ejecutor)
        requisito.refresh_from_db()
        self.assertFalse(requisito.activo)

    def test_eliminar_requisito_ya_desactivado_falla(self):
        requisito = RequisitoModalidadService.crear(
            modalidad_id=self.modalidad.pk, tipo='HORAS_MINIMAS',
            descripcion='Descripción', ejecutor=self.ejecutor, valor_numerico=120,
        )
        RequisitoModalidadService.eliminar(requisito.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            RequisitoModalidadService.eliminar(requisito.pk, ejecutor=self.ejecutor)

    def test_listar_activos_por_modalidad(self):
        requisito = RequisitoModalidadService.crear(
            modalidad_id=self.modalidad.pk, tipo='HORAS_MINIMAS',
            descripcion='Descripción', ejecutor=self.ejecutor, valor_numerico=120,
        )
        RequisitoModalidadService.eliminar(requisito.pk, ejecutor=self.ejecutor)
        resultado = RequisitoModalidadService.listar_activos_por_modalidad(self.modalidad.pk)
        self.assertEqual(resultado.count(), 0)