#apps/investigacion_formal/tests/test_proyecto_x_convocatoria.py
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.proyecto_x_convocatoria_service import (
    ProyectoXConvocatoriaService,
)


class ProyectoXConvocatoriaServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.proyecto = self._crear_proyecto()
        self.convocatoria = self._crear_convocatoria()

    def test_crear_proyecto_x_convocatoria_exitoso(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        self.assertTrue(vinculo.estado)
        self.assertFalse(vinculo.estado_finalizado_calificacion)

    def test_crear_proyecto_x_convocatoria_duplicado_falla(self):
        ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProyectoXConvocatoriaService.crear(
                convocatoria_id=self.convocatoria.pk,
                proyecto_id=self.proyecto.pk,
                ejecutor=self.ejecutor,
            )

    def test_crear_proyecto_x_convocatoria_en_convocatoria_cerrada_falla(self):
        from apps.investigacion_formal.services.convocatoria_service import ConvocatoriaService

        ConvocatoriaService.cambiar_estado(
            convocatoria_id=self.convocatoria.pk, nuevo_estado=False, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProyectoXConvocatoriaService.crear(
                convocatoria_id=self.convocatoria.pk,
                proyecto_id=self.proyecto.pk,
                ejecutor=self.ejecutor,
            )

    def test_habilitar_correccion_exitoso(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        actualizado = ProyectoXConvocatoriaService.habilitar_correccion(
            vinculo.pk, ejecutor=self.ejecutor,
        )
        self.assertTrue(actualizado.modificacion_documento_proyecto)

    def test_habilitar_correccion_ya_calificado_falla(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        vinculo.estado_finalizado_calificacion = True
        vinculo.save(update_fields=['estado_finalizado_calificacion'])

        with self.assertRaises(ValidationError):
            ProyectoXConvocatoriaService.habilitar_correccion(vinculo.pk, ejecutor=self.ejecutor)

    def test_deshabilitar_correccion_exitoso(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        ProyectoXConvocatoriaService.habilitar_correccion(vinculo.pk, ejecutor=self.ejecutor)
        actualizado = ProyectoXConvocatoriaService.deshabilitar_correccion(
            vinculo.pk, ejecutor=self.ejecutor,
        )
        self.assertFalse(actualizado.modificacion_documento_proyecto)

    def test_finalizar_calificacion_aprobado(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        actualizado = ProyectoXConvocatoriaService.finalizar_calificacion(
            proyecto_x_convocatoria_id=vinculo.pk, aprobado=True, ejecutor=self.ejecutor,
        )
        self.assertTrue(actualizado.estado_finalizado_calificacion)
        self.assertEqual(actualizado.calificacion_ultimo_filtro_calificacion, 'APROBADO')
        actualizado.proyecto.refresh_from_db()
        self.assertEqual(actualizado.proyecto.estado_aprobado, 'APROBADO')

    def test_finalizar_calificacion_ya_finalizada_falla(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        ProyectoXConvocatoriaService.finalizar_calificacion(
            proyecto_x_convocatoria_id=vinculo.pk, aprobado=True, ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            ProyectoXConvocatoriaService.finalizar_calificacion(
                proyecto_x_convocatoria_id=vinculo.pk, aprobado=False, ejecutor=self.ejecutor,
            )

    def test_eliminar_proyecto_x_convocatoria_soft_delete(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        ProyectoXConvocatoriaService.eliminar(vinculo.pk, ejecutor=self.ejecutor)
        vinculo.refresh_from_db()
        self.assertFalse(vinculo.estado)

    def test_listar_sin_calificar_no_incluye_convocatoria_activa(self):
        ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        resultado = ProyectoXConvocatoriaService.listar_sin_calificar()
        self.assertEqual(resultado.count(), 0)

    def test_listar_sin_calificar_incluye_convocatoria_cerrada(self):
        from apps.investigacion_formal.services.convocatoria_service import ConvocatoriaService

        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        ConvocatoriaService.cambiar_estado(
            convocatoria_id=self.convocatoria.pk, nuevo_estado=False, ejecutor=self.ejecutor,
        )
        resultado = ProyectoXConvocatoriaService.listar_sin_calificar()
        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first().pk, vinculo.pk)

    def test_listar_calificados_filtra_por_calificacion(self):
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=self.convocatoria.pk,
            proyecto_id=self.proyecto.pk,
            ejecutor=self.ejecutor,
        )
        ProyectoXConvocatoriaService.finalizar_calificacion(
            proyecto_x_convocatoria_id=vinculo.pk, aprobado=True, ejecutor=self.ejecutor,
        )
        resultado = ProyectoXConvocatoriaService.listar_calificados(calificacion='APROBADO')
        self.assertEqual(resultado.count(), 1)