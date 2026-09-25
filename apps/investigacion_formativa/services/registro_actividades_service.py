from django.db import transaction
from apps.investigacion_formativa.models import RegistroActividades
from apps.investigacion_formativa.selectors.registro_actividades_selector import (
    RegistroActividadesSelector,
)
from apps.investigacion_formativa.selectors.registro_horas_selector import RegistroHorasSelector
from apps.investigacion_formativa.validators.registro_actividades_validator import (
    RegistroActividadesValidator,
)
from apps.investigacion_formativa.services.registro_horas_service import RegistroHorasService
from apps.common.services.historial_service import HistorialService
from apps.investigacion_formativa.services._soporte import validar_ejecutor_autor_directo_o_gestor


class RegistroActividadesService:

    @staticmethod
    def listar():
        return RegistroActividadesSelector.listar()

    @staticmethod
    def obtener(registro_id):
        return RegistroActividadesSelector.obtener(registro_id)

    @staticmethod
    def listar_por_proceso(proceso_id):
        return RegistroActividadesSelector.listar_por_proceso(proceso_id)

    @staticmethod
    @transaction.atomic
    def crear(proceso_id, registrado_por_id, tipo_periodo, actividades, ejecutor,
              horas_reportadas=0, fecha_periodo=None, documento_id=None, nota=None):
        RegistroActividadesValidator.validar_creacion(
            proceso_id, registrado_por_id, tipo_periodo, actividades,
            horas_reportadas, fecha_periodo, documento_id, nota,
        )
        # El estudiante solo puede registrar sus propias actividades;
        # Facultad/Decano pueden registrarlas en su nombre.
        validar_ejecutor_autor_directo_o_gestor(
            registrado_por_id, ejecutor, "este registro de actividades"
        )
        registro = RegistroActividades.objects.create(
            proceso_id=proceso_id,
            registrado_por_id=registrado_por_id,
            tipo_periodo=tipo_periodo,
            actividades=actividades,
            horas_reportadas=horas_reportadas,
            fecha_periodo=fecha_periodo,
            documento_id=documento_id,
            nota=nota,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registraron actividades ({horas_reportadas} h) para el proceso "
            f"'{registro.proceso.titulo}' (id={registro.pk}).",
            objeto=registro,
        )
        return registro

    @staticmethod
    @transaction.atomic
    def actualizar(registro_id, tipo_periodo, actividades, horas_reportadas, ejecutor,
                    fecha_periodo=None, documento_id=None, nota=None):
        registro = RegistroActividadesSelector.obtener(registro_id)
        validar_ejecutor_autor_directo_o_gestor(
            registro.registrado_por_id, ejecutor, "este registro de actividades"
        )
        RegistroActividadesValidator.validar_actualizacion(
            registro, tipo_periodo, actividades, horas_reportadas, fecha_periodo, documento_id, nota
        )
        registro.tipo_periodo = tipo_periodo
        registro.actividades = actividades
        registro.horas_reportadas = horas_reportadas
        registro.fecha_periodo = fecha_periodo
        registro.documento_id = documento_id
        registro.nota = nota
        registro.save(update_fields=[
            'tipo_periodo', 'actividades', 'horas_reportadas', 'fecha_periodo', 'documento', 'nota',
        ])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el registro de actividades (id={registro.pk}) del proceso "
            f"'{registro.proceso.titulo}'.",
            objeto=registro,
        )
        return registro

    @staticmethod
    @transaction.atomic
    def aprobar(registro_id, ejecutor):
        """Sin cambios: acción exclusiva de Tutor/Facultad/Decano
        (ROLES_APROBACION_REGISTRO_ACTIVIDADES no incluye EsEstudiante),
        no requiere chequeo de autoría."""
        registro = RegistroActividadesSelector.obtener(registro_id)
        RegistroActividadesValidator.validar_aprobacion(registro)
        registro.aprobado = True
        registro.save(update_fields=['aprobado'])
        HistorialService.registrar(
            ejecutor,
            f"Se aprobó el registro de actividades (id={registro.pk}) del proceso "
            f"'{registro.proceso.titulo}' ({registro.horas_reportadas} h).",
            objeto=registro,
        )
        control_horas = RegistroHorasSelector.obtener_por_proceso(registro.proceso_id)
        if control_horas is not None:
            RegistroHorasService.recalcular(control_horas.pk, ejecutor)
        return registro

    @staticmethod
    @transaction.atomic
    def eliminar(registro_id, ejecutor):
        registro = RegistroActividadesSelector.obtener(registro_id)
        validar_ejecutor_autor_directo_o_gestor(
            registro.registrado_por_id, ejecutor, "este registro de actividades"
        )
        RegistroActividadesValidator.validar_eliminacion(registro)
        registro.activo = False
        registro.save(update_fields=['activo'])
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó el registro de actividades del proceso "
            f"'{registro.proceso.titulo}' (id={registro.pk}).",
            objeto=registro,
        )
        return registro