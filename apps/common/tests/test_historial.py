from django.utils import timezone
from datetime import timedelta
from django.test import TestCase
from .base import CommonFixturesMixin
from apps.common.services.historial_service import HistorialService


class HistorialServiceTests(CommonFixturesMixin, TestCase):

    def test_registrar_sin_objeto(self):
        registro = HistorialService.registrar(self.ejecutor, "Inicio de sesión exitoso.")
        self.assertIsNone(registro.content_type)
        self.assertIsNone(registro.object_id)

    def test_registrar_con_objeto(self):
        registro = HistorialService.registrar(
            self.ejecutor, "Se actualizó la facultad de pruebas.", objeto=self.objeto_generico
        )
        self.assertEqual(registro.object_id, self.objeto_generico.pk)
        self.assertEqual(registro.objeto_relacionado, self.objeto_generico)

    def test_registrar_accion_sistema_sin_usuario(self):
        registro = HistorialService.registrar(None, "[SISTEMA] Proceso automático ejecutado.")
        self.assertIsNone(registro.usuario)

    def test_listar_devuelve_todos_los_registros(self):
        HistorialService.registrar(self.ejecutor, "Acción 1")
        HistorialService.registrar(self.ejecutor, "Acción 2")
        self.assertEqual(HistorialService.listar().count(), 2)

    def test_obtener_y_buscar(self):
        registro = HistorialService.registrar(self.ejecutor, "Acción única")
        self.assertEqual(HistorialService.obtener(registro.pk).pk, registro.pk)
        self.assertEqual(HistorialService.buscar(registro.pk).pk, registro.pk)
        self.assertIsNone(HistorialService.buscar(999999))

    def test_listar_por_usuario(self):
        HistorialService.registrar(self.ejecutor, "Acción del ejecutor")
        HistorialService.registrar(self.otro_usuario, "Acción del revisor")
        resultados = HistorialService.listar_por_usuario(self.ejecutor.pk)
        self.assertEqual(resultados.count(), 1)

    def test_listar_acciones_sistema(self):
        HistorialService.registrar(self.ejecutor, "Acción de usuario")
        HistorialService.registrar(None, "[SISTEMA] Acción automática")
        resultados = HistorialService.listar_acciones_sistema()
        self.assertEqual(resultados.count(), 1)
        self.assertIsNone(resultados.first().usuario)

    def test_listar_por_objeto(self):
        HistorialService.registrar(
            self.ejecutor, "Acción sobre la facultad de pruebas", objeto=self.objeto_generico
        )
        otro_objeto = self._crear_objeto_generico(nombre='Facultad B', abreviatura='FB')
        HistorialService.registrar(self.ejecutor, "Acción sobre otra facultad", objeto=otro_objeto)
        resultados = HistorialService.listar_por_objeto(self.objeto_generico)
        self.assertEqual(resultados.count(), 1)

    def test_listar_por_modelo(self):
        from apps.institucional.models import FacultadEscuela
        HistorialService.registrar(self.ejecutor, "Acción 1", objeto=self.objeto_generico)
        resultados = HistorialService.listar_por_modelo(FacultadEscuela)
        self.assertEqual(resultados.count(), 1)

    def test_listar_por_rango_fechas(self):
        HistorialService.registrar(self.ejecutor, "Acción reciente")
        ahora = timezone.now()
        resultados = HistorialService.listar_por_rango_fechas(
            ahora - timedelta(days=1), ahora + timedelta(days=1)
        )
        self.assertEqual(resultados.count(), 1)

    def test_buscar_por_accion(self):
        HistorialService.registrar(self.ejecutor, "Se aprobó el documento X")
        HistorialService.registrar(self.ejecutor, "Se rechazó el documento Y")
        resultados = HistorialService.buscar_por_accion("aprobó")
        self.assertEqual(resultados.count(), 1)