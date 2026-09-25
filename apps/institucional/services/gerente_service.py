"""
Service de Gerente.

Interfaz estándar definitiva: listar(), obtener(id), crear(...),
actualizar(id, ...), eliminar(id). 'crear()' ES el método público de
asignación — no existe un método separado 'asignar_nuevo_gerente()'
(corrección aplicada según punto 8 del consenso: la inconsistencia de
tener crear() Y asignar_nuevo_gerente() por separado rompía la
uniformidad de la interfaz).

'crear()' incorpora la regla de negocio confirmada explícitamente:
si existe un Gerente activo, se cierra automáticamente (fecha_salida=
fecha_ingreso del nuevo, estado=False) antes de crear el nuevo registro.
Todo dentro de @transaction.atomic para que no quede un estado
intermedio inconsistente.

Métodos especializados (operaciones de negocio específicas, no parte
del CRUD genérico): obtener_actual(), finalizar().
"""
from django.db import transaction
from django.utils import timezone
from apps.institucional.models import Gerente
from apps.institucional.selectors.gerente_selector import GerenteSelector
from apps.institucional.validators.gerente_validator import GerenteValidator
from apps.common.services.historial_service import HistorialService
_NO_PROVISTO = object()


class GerenteService:

    @staticmethod
    def listar():
        return GerenteSelector.listar()

    @staticmethod
    def obtener(gerente_id):
        return GerenteSelector.obtener(gerente_id)

    @staticmethod
    @transaction.atomic
    def crear(persona_id, ejecutor, fecha_ingreso=None):
        """
        Asigna un nuevo Gerente. Si hay uno vigente, lo cierra primero
        de forma atómica. Este es el ÚNICO punto de entrada para crear
        un Gerente — no existe un método separado de "reemplazo".
        """
        fecha_ingreso = fecha_ingreso or timezone.now().date()
        GerenteValidator.validar_creacion(persona_id, fecha_ingreso, fecha_salida=None)

        gerente_actual = GerenteSelector.obtener_actual()
        if gerente_actual is not None:
            gerente_actual.fecha_salida = fecha_ingreso
            gerente_actual.estado = False
            gerente_actual.save(update_fields=["fecha_salida", "estado"])
            HistorialService.registrar(
                ejecutor,
                f"Se cerró la gerencia de '{gerente_actual.persona}' "
                f"(id={gerente_actual.pk}) por reemplazo.",
                objeto=gerente_actual,
            )

        nuevo_gerente = Gerente.objects.create(
            persona_id=persona_id,
            fecha_ingreso=fecha_ingreso,
            fecha_salida=None,
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se asignó a '{nuevo_gerente.persona}' como nuevo Gerente "
            f"(id={nuevo_gerente.pk}).",
            objeto=nuevo_gerente,
        )
        return nuevo_gerente

    @staticmethod
    @transaction.atomic
    def actualizar(gerente_id, ejecutor, fecha_ingreso=_NO_PROVISTO, fecha_salida=_NO_PROVISTO):
        """
        Edición de datos administrativos (corrección de fechas) sin pasar
        por la semántica de reemplazo de crear().
        """
        gerente = GerenteSelector.obtener(gerente_id)
        nueva_fecha_ingreso = gerente.fecha_ingreso if fecha_ingreso is _NO_PROVISTO else fecha_ingreso
        nueva_fecha_salida = gerente.fecha_salida if fecha_salida is _NO_PROVISTO else fecha_salida
        GerenteValidator.validar_actualizacion(gerente, nueva_fecha_ingreso, nueva_fecha_salida)
        gerente.fecha_ingreso = nueva_fecha_ingreso
        gerente.fecha_salida = nueva_fecha_salida
        gerente.estado = nueva_fecha_salida is None
        gerente.save(update_fields=["fecha_ingreso", "fecha_salida", "estado"])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizaron las fechas de la gerencia de "
            f"'{gerente.persona}' (id={gerente.pk}).",
            objeto=gerente,
        )
        return gerente

    @staticmethod
    @transaction.atomic
    def eliminar(gerente_id, ejecutor):
        """
        SOFT-DELETE. Marca estado=False sin necesariamente registrar
        fecha_salida (a diferencia de finalizar()). Pensado para corregir
        registros creados por error, no para representar el fin natural
        de un periodo de gestión.
        """
        gerente = GerenteSelector.obtener(gerente_id)
        GerenteValidator.validar_eliminacion(gerente)
        gerente.estado = False
        gerente.save(update_fields=["estado"])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) el registro de gerencia de "
            f"'{gerente.persona}' (id={gerente.pk}).",
            objeto=gerente,
        )
        return gerente

    @staticmethod
    def obtener_actual():
        return GerenteSelector.obtener_actual()

    @staticmethod
    @transaction.atomic
    def finalizar(gerente_id, ejecutor, fecha_salida=None):
        """
        Cierra manualmente un periodo de gerencia (fin natural de la
        gestión), dejando el cargo vacante. Distinto de eliminar(): aquí
        sí se registra fecha_salida.
        """
        gerente = GerenteSelector.obtener(gerente_id)
        fecha_salida = fecha_salida or timezone.now().date()
        GerenteValidator.validar_actualizacion(gerente, gerente.fecha_ingreso, fecha_salida)
        gerente.fecha_salida = fecha_salida
        gerente.estado = False
        gerente.save(update_fields=["fecha_salida", "estado"])
        HistorialService.registrar(
            ejecutor,
            f"Se finalizó la gerencia de '{gerente.persona}' "
            f"(id={gerente.pk}), con fecha de salida {fecha_salida}.",
        )
        return gerente