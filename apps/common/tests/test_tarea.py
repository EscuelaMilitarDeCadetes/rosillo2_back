from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from .base import CommonFixturesMixin
from apps.common.services.tarea_service import TareaService


class TareaServiceTests(CommonFixturesMixin, TestCase):

    def test_crear_tarea_exitoso(self):
        tarea = TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Revisar informe mensual',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() + timedelta(days=5)).date(),
        )
        self.assertFalse(tarea.completada)
        self.assertEqual(tarea.objeto_relacionado, self.objeto_generico)

    def test_crear_tarea_sin_asignado_falla(self):
        with self.assertRaises(ValidationError):
            TareaService.crear(
                asignado_a_id=None,
                descripcion='Revisar informe',
                objeto=self.objeto_generico,
                ejecutor=self.ejecutor,
            )

    def test_crear_tarea_descripcion_vacia_falla(self):
        with self.assertRaises(ValidationError):
            TareaService.crear(
                asignado_a_id=self.otro_usuario.pk,
                descripcion='   ',
                objeto=self.objeto_generico,
                ejecutor=self.ejecutor,
            )

    def test_reasignar_tarea_exitoso(self):
        tarea = TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Revisar informe mensual',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
        )
        from apps.usuarios.models import Usuario
        nuevo = Usuario.objects.create_user(
            username='nuevo@esmic.edu.co', email='nuevo@esmic.edu.co', password='clave123'
        )
        reasignada = TareaService.reasignar(tarea.pk, nuevo.pk, ejecutor=self.ejecutor)
        self.assertEqual(reasignada.asignado_a_id, nuevo.pk)

    def test_completar_tarea_exitoso(self):
        tarea = TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Revisar informe mensual',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
        )
        completada = TareaService.completar(tarea.pk, ejecutor=self.otro_usuario)
        self.assertTrue(completada.completada)

    def test_completar_tarea_ya_completada_falla(self):
        tarea = TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Revisar informe mensual',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
        )
        TareaService.completar(tarea.pk, ejecutor=self.otro_usuario)
        with self.assertRaises(ValidationError):
            TareaService.completar(tarea.pk, ejecutor=self.otro_usuario)

    def test_listar_por_usuario_solo_pendientes(self):
        t1 = TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea 1',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
        )
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea 2',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
        )
        TareaService.completar(t1.pk, ejecutor=self.otro_usuario)
        pendientes = TareaService.listar_por_usuario(self.otro_usuario.pk, solo_pendientes=True)
        self.assertEqual(pendientes.count(), 1)

    def test_listar_por_objeto(self):
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea sobre la facultad de pruebas',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
        )
        otro_objeto = self._crear_objeto_generico(nombre='Facultad C', abreviatura='FC')
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea sobre otra facultad',
            objeto=otro_objeto,
            ejecutor=self.ejecutor,
        )
        resultados = TareaService.listar_por_objeto(self.objeto_generico)
        self.assertEqual(resultados.count(), 1)

    def test_listar_vencidas(self):
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea vencida',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() - timedelta(days=3)).date(),
        )
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea futura',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() + timedelta(days=3)).date(),
        )
        vencidas = TareaService.listar_vencidas()
        self.assertEqual(vencidas.count(), 1)

    def test_listar_proximas_a_vencer(self):
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea próxima',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() + timedelta(days=2)).date(),
        )
        TareaService.crear(
            asignado_a_id=self.otro_usuario.pk,
            descripcion='Tarea lejana',
            objeto=self.objeto_generico,
            ejecutor=self.ejecutor,
            fecha_limite=(timezone.now() + timedelta(days=30)).date(),
        )
        proximas = TareaService.listar_proximas_a_vencer(dias=3)
        self.assertEqual(proximas.count(), 1)