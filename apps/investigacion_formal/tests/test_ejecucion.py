from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .base import InvestigacionFormalFixturesMixin
from apps.investigacion_formal.services.ejecucion_service import EjecucionService
from apps.investigacion_formal.selectors.monto_selector import MontoSelector


class EjecucionServiceTests(InvestigacionFormalFixturesMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.tipo_rubro = self._crear_tipo_rubro()
        self.monto = self._crear_monto(solicitado=1000000)
        self.monto.aprobado = 1000000
        self.monto.save(update_fields=['aprobado'])

    def test_crear_ejecucion_exitoso_actualiza_ejecutado_del_monto(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Compra de equipos',
            costo=200000,
            descripcion='Equipos de laboratorio',
            ejecutor=self.ejecutor,
        )
        self.assertTrue(ejecucion.estado)
        self.monto.refresh_from_db()
        self.assertEqual(self.monto.ejecutado, 200000)

    def test_crear_ejecucion_que_excede_presupuesto_falla(self):
        with self.assertRaises(ValidationError):
            EjecucionService.crear(
                monto_id=self.monto.pk,
                tipo_rubro_id=self.tipo_rubro.pk,
                nombre='Gasto excesivo',
                costo=2000000,
                descripcion='Supera el aprobado',
                ejecutor=self.ejecutor,
            )

    def test_crear_ejecucion_costo_negativo_falla(self):
        with self.assertRaises(ValidationError):
            EjecucionService.crear(
                monto_id=self.monto.pk,
                tipo_rubro_id=self.tipo_rubro.pk,
                nombre='Gasto inválido',
                costo=-100,
                descripcion='Costo negativo',
                ejecutor=self.ejecutor,
            )

    def test_actualizar_ejecucion_incrementa_diferencia_en_monto(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Gasto inicial',
            costo=100000,
            descripcion='Descripción inicial',
            ejecutor=self.ejecutor,
        )
        EjecucionService.actualizar(
            ejecucion_id=ejecucion.pk,
            ejecutor=self.ejecutor,
            costo=150000,
        )
        self.monto.refresh_from_db()
        self.assertEqual(self.monto.ejecutado, 150000)

    def test_actualizar_ejecucion_que_excede_presupuesto_falla(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Gasto inicial',
            costo=100000,
            descripcion='Descripción inicial',
            ejecutor=self.ejecutor,
        )
        with self.assertRaises(ValidationError):
            EjecucionService.actualizar(
                ejecucion_id=ejecucion.pk,
                ejecutor=self.ejecutor,
                costo=2000000,
            )

    def test_eliminar_ejecucion_revierte_costo_del_monto(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Gasto a eliminar',
            costo=100000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        EjecucionService.eliminar(ejecucion.pk, ejecutor=self.ejecutor)

        ejecucion.refresh_from_db()
        self.assertFalse(ejecucion.estado)
        self.monto.refresh_from_db()
        self.assertEqual(self.monto.ejecutado, 0)

    def test_eliminar_ejecucion_ya_desactivada_falla(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Gasto doble baja',
            costo=50000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        EjecucionService.eliminar(ejecucion.pk, ejecutor=self.ejecutor)
        with self.assertRaises(ValidationError):
            EjecucionService.eliminar(ejecucion.pk, ejecutor=self.ejecutor)

    def test_listar_por_monto_solo_activas(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Activa',
            costo=50000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='A eliminar',
            costo=50000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        eliminar = MontoSelector.obtener(self.monto.pk)
        resultado = EjecucionService.listar_por_monto(self.monto.pk, solo_activas=True)
        self.assertEqual(resultado.count(), 2)
        
    def test_actualizar_solo_costo(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Inicial',
            costo=100000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        EjecucionService.actualizar(
            ejecucion.pk,
            ejecutor=self.ejecutor,
            costo=150000,
        )
        self.monto.refresh_from_db()
        self.assertEqual(
            self.monto.ejecutado,
            150000
        )

    def test_actualizar_solo_monto(self):
        monto2 = self._crear_monto(solicitado=1000000)
        monto2.aprobado = 1000000
        monto2.save(update_fields=['aprobado'])
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Inicial',
            costo=100000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        EjecucionService.actualizar(
            ejecucion.pk,
            ejecutor=self.ejecutor,
            monto_id=monto2.pk,
        )
        self.monto.refresh_from_db()
        monto2.refresh_from_db()
        self.assertEqual(self.monto.ejecutado, 0)
        self.assertEqual(monto2.ejecutado, 100000)

    def test_actualizar_monto_y_costo(self):
        monto2 = self._crear_monto(solicitado=1000000)
        monto2.aprobado = 1000000
        monto2.save(update_fields=['aprobado'])
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Inicial',
            costo=100000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        EjecucionService.actualizar(
            ejecucion.pk,
            ejecutor=self.ejecutor,
            monto_id=monto2.pk,
            costo=250000,
        )
        self.monto.refresh_from_db()
        monto2.refresh_from_db()
        self.assertEqual(self.monto.ejecutado, 0)
        self.assertEqual(monto2.ejecutado, 250000)

    def test_actualizar_sin_cambios(self):
        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Inicial',
            costo=100000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )
        EjecucionService.actualizar(
            ejecucion.pk,
            ejecutor=self.ejecutor,
        )
        self.monto.refresh_from_db()
        self.assertEqual(
            self.monto.ejecutado,
            100000
        )
        
    def test_no_permite_mover_ejecucion_a_otro_proyecto(self):
        proyecto2 = self._crear_proyecto(
            titulo='Proyecto 2'
        )

        monto_otro_proyecto = self._crear_monto(
            proyecto=proyecto2,
            solicitado=1000000,
        )
        monto_otro_proyecto.aprobado = 1000000
        monto_otro_proyecto.save(update_fields=['aprobado'])

        ejecucion = EjecucionService.crear(
            monto_id=self.monto.pk,
            tipo_rubro_id=self.tipo_rubro.pk,
            nombre='Inicial',
            costo=100000,
            descripcion='Descripción',
            ejecutor=self.ejecutor,
        )

        with self.assertRaises(ValidationError) as ctx:
            EjecucionService.actualizar(
                ejecucion.pk,
                ejecutor=self.ejecutor,
                monto_id=monto_otro_proyecto.pk,
            )

        self.assertIn(
            "La ejecución no puede cambiarse a un monto perteneciente a otro proyecto.",
            str(ctx.exception),
        )            