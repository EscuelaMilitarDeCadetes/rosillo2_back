#apps/investigacion_formal/services/proyecto_service.py
from datetime import datetime

from django.db import transaction

from apps.common.services.tarea_service import TareaService
from apps.investigacion_formal.models import Proyecto
from apps.investigacion_formal.selectors.proyecto_selector import ProyectoSelector
from apps.institucional.models import PersonaXGrupo
from apps.investigacion_formal.validators.proyecto_validator import ProyectoValidator
from apps.common.services.historial_service import HistorialService
from django.utils import timezone
from apps.investigacion_formal.models import Monto
from apps.investigacion_formal.selectors.convocatoria_selector import ConvocatoriaSelector
from apps.investigacion_formal.services.convocatoria_service import ConvocatoriaService
from apps.investigacion_formal.services.proyecto_x_convocatoria_service import (
    ProyectoXConvocatoriaService,
)


class ProyectoService:

    @staticmethod
    def listar():
        return ProyectoSelector.listar()

    @staticmethod
    def listar_activos():
        return ProyectoSelector.listar_activos()

    @staticmethod
    def obtener(proyecto_id):
        return ProyectoSelector.obtener(proyecto_id)

    @staticmethod
    def listar_por_estado_aprobado(estado_aprobado):
        return ProyectoSelector.listar_por_estado_aprobado(estado_aprobado)

    @staticmethod
    @transaction.atomic
    def crear(usuario_id, gerente_id, titulo, interno, alianza, financiado,
            unidad_ejecutora, linea_investigacion, ejecutor, codigo=None,
            estado_aprobado='SIN_CALIFICAR', fecha_inicio=None, fecha_fin=None):
        """
        codigo=None            -> proyecto NUEVO: el código se genera automáticamente
                                la primera vez que se llame a asignar_timeline().
        codigo='ING2019-I03'   -> carga de REPOSITORIO histórico: se respeta el
                                código ya existente y nunca se regenera.
        """
        ProyectoValidator.validar_creacion(
            usuario_id, gerente_id, titulo, interno, alianza, financiado,
            unidad_ejecutora, linea_investigacion,
            estado_aprobado=estado_aprobado, codigo=codigo,
        )
        proyecto = Proyecto.objects.create(
            usuario_id=usuario_id,
            gerente_id=gerente_id,
            titulo=titulo.strip(),
            interno=interno,
            registro_acta_cierre=False,
            alianza=alianza,
            estado=True,
            estado_aprobado=estado_aprobado,
            financiado=financiado,
            unidad_ejecutora=unidad_ejecutora.strip(),
            linea_investigacion=linea_investigacion.strip(),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            codigo=(codigo or '').strip(),
            gruplac=False,
        )
        if codigo:
            HistorialService.registrar(
                ejecutor,
                f"Se importó al repositorio el proyecto '{proyecto.titulo}' "
                f"con código histórico '{proyecto.codigo}' (id={proyecto.pk}).",
                objeto=proyecto,
            )
        else:
            HistorialService.registrar(
                ejecutor,
                f"Se creó el proyecto '{proyecto.titulo}' (id={proyecto.pk}).",
                objeto=proyecto,
            )
        return proyecto

    @staticmethod
    @transaction.atomic
    def actualizar(proyecto_id, titulo, unidad_ejecutora, linea_investigacion, ejecutor):
        """Exclusivo de CINTERNO/CEXTERNO."""
        proyecto = ProyectoSelector.obtener(proyecto_id)
        ProyectoValidator.validar_actualizacion(
            proyecto_id, titulo, unidad_ejecutora, linea_investigacion
        )
        proyecto.titulo = titulo.strip()
        proyecto.unidad_ejecutora = unidad_ejecutora.strip()
        proyecto.linea_investigacion = linea_investigacion.strip()
        proyecto.save(update_fields=['titulo', 'unidad_ejecutora', 'linea_investigacion'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el proyecto '{proyecto.titulo}' (id={proyecto.pk}).",
            objeto=proyecto,
        )
        return proyecto

    @staticmethod
    @transaction.atomic
    def asignar_timeline(proyecto_id, fecha_inicio, fecha_fin, ejecutor):
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        proyecto = ProyectoSelector.obtener(proyecto_id)
        ProyectoValidator.validar_asignacion_timeline(fecha_inicio, fecha_fin)
        proyecto.fecha_inicio = fecha_inicio
        proyecto.fecha_fin = fecha_fin
        campos_a_guardar = ['fecha_inicio', 'fecha_fin']

        # Regla de repositorio: si el proyecto YA tiene código (carga histórica,
        # o ya se le generó antes), nunca se regenera ni se sobreescribe.
        if not proyecto.codigo:
            anio = fecha_inicio.year
            pxg = (
                PersonaXGrupo.objects
                .filter(
                    persona__asignaciones__usuario_id=proyecto.usuario_id,
                    persona__asignaciones__estado=True,
                    estado=True,
                )
                .select_related('facultad', 'grupo')
                .first()
            )
            if pxg and pxg.facultad_id:
                sigla = pxg.facultad.abreviatura
            elif pxg and pxg.grupo_id:
                sigla = pxg.grupo.sigla_grupo
            else:
                sigla = proyecto.unidad_ejecutora
            prefijo = f"{sigla}{anio}-{'I' if proyecto.interno else 'E'}"
            cantidad = ProyectoSelector.contar_aprobados_por_prefijo(prefijo)
            proyecto.codigo = f"{prefijo}{cantidad + 1:02d}"
            campos_a_guardar.append('codigo')
        proyecto.save(update_fields=campos_a_guardar)
        TareaService.crear_recordatorio(
            usuario_id=proyecto.usuario_id,
            descripcion=(
                f"Agregar investigadores, productos y objetivos/puntos de control "
                f"al proyecto '{proyecto.titulo}'"
            ),
            objeto=proyecto,
            ejecutor=ejecutor,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se asignó el tiempo de ejecución al proyecto '{proyecto.titulo}' "
            f"(código={proyecto.codigo}).",
            objeto=proyecto,
        )
        return proyecto

    @staticmethod
    @transaction.atomic
    def editar_fecha_cierre(proyecto_id, nueva_fecha_fin, ejecutor):
        """Réplica de editarFechaCierre."""
        if isinstance(nueva_fecha_fin, str):
            nueva_fecha_fin = datetime.strptime(nueva_fecha_fin, '%Y-%m-%d').date()
        proyecto = ProyectoSelector.obtener(proyecto_id)
        ProyectoValidator.validar_edicion_fecha_cierre(proyecto, nueva_fecha_fin)
        proyecto.fecha_fin = nueva_fecha_fin
        proyecto.save(update_fields=['fecha_fin'])
        HistorialService.registrar(
            ejecutor,
            f"Se cambió la fecha de cierre del proyecto '{proyecto.titulo}' "
            f"a {nueva_fecha_fin}.",
            objeto=proyecto,
        )
        return proyecto

    @staticmethod
    @transaction.atomic
    def cambiar_estado_aprobado(proyecto_id, nuevo_estado_aprobado, ejecutor):
        proyecto = ProyectoSelector.obtener(proyecto_id)
        ProyectoValidator.validar_cambio_estado_aprobado(nuevo_estado_aprobado)
        proyecto.estado_aprobado = nuevo_estado_aprobado
        proyecto.save(update_fields=['estado_aprobado'])
        HistorialService.registrar(
            ejecutor,
            f"Se cambió el estado de aprobación del proyecto '{proyecto.titulo}' "
            f"a {nuevo_estado_aprobado}.",
            objeto=proyecto,
        )
        return proyecto

    @staticmethod
    @transaction.atomic
    def subir_a_gruplac(proyecto_id, ejecutor):
        proyecto = ProyectoSelector.obtener(proyecto_id)
        ProyectoValidator.validar_subida_gruplac(proyecto)
        proyecto.gruplac = True
        proyecto.save(update_fields=['gruplac'])
        HistorialService.registrar(
            ejecutor,
            f"Se cargó el proyecto '{proyecto.titulo}' al GrupLAC.",
            objeto=proyecto,
        )
        return proyecto

    @staticmethod
    @transaction.atomic
    def registrar_acta_cierre(proyecto_id, ejecutor):
        proyecto = ProyectoSelector.obtener(proyecto_id)
        ProyectoValidator.validar_registro_acta_cierre(proyecto)
        proyecto.registro_acta_cierre = True
        proyecto.estado = False
        proyecto.save(update_fields=['registro_acta_cierre', 'estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se registró el acta de cierre del proyecto '{proyecto.titulo}' "
            f"y se cerró definitivamente.",
            objeto=proyecto,
        )
        return proyecto

    @staticmethod
    @transaction.atomic
    def eliminar(proyecto_id, ejecutor):
        """Soft-delete; exclusivo de CINTERNO/CEXTERNO."""
        proyecto = ProyectoSelector.obtener(proyecto_id)
        ProyectoValidator.validar_eliminacion(proyecto)
        proyecto.estado = False
        proyecto.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó el proyecto '{proyecto.titulo}' (id={proyecto.pk}).",
            objeto=proyecto,
        )
        return proyecto    
    
    @staticmethod
    @transaction.atomic
    def crear_proyecto_externo(usuario_id, gerente_id, titulo, unidad_ejecutora,
                               linea_investigacion, entidad, valor_solicitado,
                               alianza, financiado, ejecutor,
                               grupo_investigacion_id=None, facultad_id=None):
        """
        Los proyectos de convocatoria externa se aprueban
        automáticamente, sin pasar por las 6 fases de Calificacion que sí
        aplican a los proyectos internos.
        grupo_investigacion_id/facultad_id reemplazan la derivación
        automática desde PersonaXGrupo del usuario creador (CEXTERNO), que
        no aplica a proyectos externos porque esa cuenta no representa
        ninguna facultad/grupo real.
        """
        grupo, facultad_id_valido = ProyectoValidator.validar_responsable_externo(
            grupo_investigacion_id, facultad_id,
        )
        anio_actual = timezone.now().year
        nombre_convocatoria_externa = f"{entidad} {anio_actual}"
        convocatoria = ConvocatoriaSelector.buscar_por_nombre(nombre_convocatoria_externa)
        if convocatoria is None:
            convocatoria = ConvocatoriaService.crear(
                nombre_convocatoria=nombre_convocatoria_externa,
                anio_convocatoria=anio_actual,
                inicio=timezone.now().date(),
                cierre=timezone.now().date(),
                interno=False,
                ejecutor=ejecutor,
            )
            ConvocatoriaService.cambiar_estado(
                convocatoria_id=convocatoria.pk, nuevo_estado=False, ejecutor=ejecutor,
            )
        proyecto = ProyectoService.crear(
            usuario_id=usuario_id,
            gerente_id=gerente_id,
            titulo=titulo,
            interno=False,
            alianza=alianza,
            financiado=financiado,
            unidad_ejecutora=unidad_ejecutora,
            linea_investigacion=linea_investigacion,
            ejecutor=ejecutor,
            estado_aprobado='APROBADO',
        )
        #Fija el responsable institucional del proyecto externo.
        proyecto.grupo_investigacion_id = grupo.pk
        proyecto.facultad_id = facultad_id_valido
        proyecto.save(update_fields=['grupo_investigacion', 'facultad'])
        Monto.objects.create(
            proyecto=proyecto,
            solicitado=valor_solicitado or 0,
            aprobado=valor_solicitado or 0,
            asignado=timezone.now().date(),
            ejecutado=0,
            contrapartida=0,
            total=valor_solicitado or 0,
        )
        ProyectoXConvocatoriaService.crear_ya_finalizado_aprobado(
            proyecto_id=proyecto.pk,
            convocatoria_id=convocatoria.pk,
            ejecutor=ejecutor,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó el proyecto externo '{proyecto.titulo}' con aprobación "
            f"automática (entidad='{entidad}', grupo='{grupo.sigla_grupo}'"
            f"{', facultad=' + str(facultad_id_valido) if facultad_id_valido else ''}).",
            objeto=proyecto,
        )
        return proyecto
