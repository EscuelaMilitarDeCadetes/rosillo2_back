# apps/investigacion_formal/services/proyecto_x_convocatoria_service.py
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.investigacion_formal.models import ProyectoXConvocatoria
from apps.investigacion_formal.selectors.proyecto_x_convocatoria_selector import (
    ProyectoXConvocatoriaSelector,
)
from apps.investigacion_formal.validators.proyecto_x_convocatoria_validator import (
    ProyectoXConvocatoriaValidator,
)
from apps.common.services.historial_service import HistorialService

from apps.institucional.selectors.gerente_selector import GerenteSelector
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector
from apps.common.services.documento_firma_service import DocumentoFirmaService
from apps.investigacion_formal.services.monto_service import MontoService
from apps.investigacion_formal.services.calificacion_service import CalificacionService
from apps.investigacion_formal.selectors.tipo_calificacion_selector import TipoCalificacionSelector


class ProyectoXConvocatoriaService:

    @staticmethod
    def listar():
        return ProyectoXConvocatoriaSelector.listar()

    @staticmethod
    def obtener(proyecto_x_convocatoria_id):
        return ProyectoXConvocatoriaSelector.obtener(proyecto_x_convocatoria_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return ProyectoXConvocatoriaSelector.listar_por_proyecto(proyecto_id)

    @staticmethod
    def listar_por_convocatoria(convocatoria_id):
        return ProyectoXConvocatoriaSelector.listar_por_convocatoria(convocatoria_id)

    @staticmethod
    def listar_sin_calificar():
        return ProyectoXConvocatoriaSelector.listar_sin_calificar()

    @staticmethod
    def listar_calificados(calificacion=None):
        return ProyectoXConvocatoriaSelector.listar_calificados(calificacion=calificacion)

    @staticmethod
    def listar_por_facultad(facultad_id):
        return ProyectoXConvocatoriaSelector.listar_por_facultad(facultad_id)

    @staticmethod
    def listar_por_grupo(grupo_id):
        return ProyectoXConvocatoriaSelector.listar_por_grupo(grupo_id)
    
    @staticmethod
    def listar_por_usuario(usuario_id):
        return ProyectoXConvocatoriaSelector.listar_por_usuario(usuario_id)

    @staticmethod
    @transaction.atomic
    def crear(convocatoria_id, proyecto_id, ejecutor):
        """Réplica de participarConvocatoria: FACULTAD/GRUPO postulan un
        proyecto ya creado a una convocatoria activa."""
        ProyectoXConvocatoriaValidator.validar_creacion(convocatoria_id, proyecto_id)
        vinculo = ProyectoXConvocatoria.objects.create(
            convocatoria_id=convocatoria_id,
            proyecto_id=proyecto_id,
            estado=True,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se postuló el proyecto '{vinculo.proyecto.titulo}' a la "
            f"convocatoria '{vinculo.convocatoria.nombre_convocatoria}' "
            f"(id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def habilitar_correccion(proyecto_x_convocatoria_id, ejecutor):
        """Réplica de habilitarCorreccionDoc; exclusivo de CINTERNO/CEXTERNO."""
        vinculo = ProyectoXConvocatoriaSelector.obtener(proyecto_x_convocatoria_id)
        ProyectoXConvocatoriaValidator.validar_habilitar_correccion(vinculo)
        vinculo.modificacion_documento_proyecto = True
        vinculo.save(update_fields=['modificacion_documento_proyecto'])
        HistorialService.registrar(
            ejecutor,
            f"Se habilitó la corrección de documentos del proyecto "
            f"'{vinculo.proyecto.titulo}' en la convocatoria "
            f"'{vinculo.convocatoria.nombre_convocatoria}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def deshabilitar_correccion(proyecto_x_convocatoria_id, ejecutor):
        """Réplica de desHabilitarCorreccionDoc."""
        vinculo = ProyectoXConvocatoriaSelector.obtener(proyecto_x_convocatoria_id)
        ProyectoXConvocatoriaValidator.validar_deshabilitar_correccion(vinculo)
        vinculo.modificacion_documento_proyecto = False
        vinculo.save(update_fields=['modificacion_documento_proyecto'])
        HistorialService.registrar(
            ejecutor,
            f"Se deshabilitó la corrección de documentos del proyecto "
            f"'{vinculo.proyecto.titulo}' en la convocatoria "
            f"'{vinculo.convocatoria.nombre_convocatoria}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def finalizar_calificacion(proyecto_x_convocatoria_id, aprobado, ejecutor):
        """Marca la calificación de las 6 fases como finalizada, en línea con lo
        que CalificacionService.calificar_fase ya deja en estado_finalizado_calificacion,
        para casos donde se requiera forzar el cierre manualmente."""
        vinculo = ProyectoXConvocatoriaSelector.obtener(proyecto_x_convocatoria_id)
        ProyectoXConvocatoriaValidator.validar_finalizar_calificacion(vinculo, aprobado)
        vinculo.estado_finalizado_calificacion = True
        vinculo.calificacion_ultimo_filtro_calificacion = (
            'APROBADO' if aprobado else 'NO_APROBADO'
        )
        vinculo.save(update_fields=[
            'estado_finalizado_calificacion', 'calificacion_ultimo_filtro_calificacion',
        ])
        proyecto = vinculo.proyecto
        proyecto.estado_aprobado = 'APROBADO' if aprobado else 'NO_APROBADO'
        proyecto.save(update_fields=['estado_aprobado'])
        HistorialService.registrar(
            ejecutor,
            f"Se finalizó la calificación del proyecto '{vinculo.proyecto.titulo}' "
            f"en la convocatoria '{vinculo.convocatoria.nombre_convocatoria}' "
            f"como {'APROBADO' if aprobado else 'NO APROBADO'}.",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def eliminar(proyecto_x_convocatoria_id, ejecutor):
        """Soft-delete; exclusivo de CINTERNO/CEXTERNO."""
        vinculo = ProyectoXConvocatoriaSelector.obtener(proyecto_x_convocatoria_id)
        ProyectoXConvocatoriaValidator.validar_eliminacion(vinculo)
        vinculo.estado = False
        vinculo.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó la participación del proyecto "
            f"'{vinculo.proyecto.titulo}' en la convocatoria "
            f"'{vinculo.convocatoria.nombre_convocatoria}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo
    
    @staticmethod
    @transaction.atomic
    def crear_ya_finalizado_aprobado(proyecto_id, convocatoria_id, ejecutor):
        """
        Variante de crear() para proyectos que nacen ya aprobados (hoy,
        únicamente proyectos externos vía ProyectoService.crear_proyecto_externo).
        No pasa por calificar_fase: se marca directamente como finalizado
        y aprobado en ambos filtros, replicando el comportamiento del
        Thymeleaf original para convocatorias externas.
        """
        ProyectoXConvocatoriaValidator.validar_creacion_ya_finalizado(convocatoria_id, proyecto_id)
        aplicar = ProyectoXConvocatoria.objects.create(
            proyecto_id=proyecto_id,
            convocatoria_id=convocatoria_id,
            estado=True,
            estado_finalizado_calificacion=True,
            ultimo_filtro_calificacion='APROBADO',
            calificacion_ultimo_filtro_calificacion='APROBADO',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se vinculó el proyecto id={proyecto_id} a la convocatoria "
            f"id={convocatoria_id}, ya aprobado (proyecto externo).",
            objeto=aplicar,
        )
        return aplicar
    
    @staticmethod
    def buscar_con_filtros(**filtros):
        return ProyectoXConvocatoriaSelector.buscar_con_filtros(**filtros)
    
    @staticmethod
    @transaction.atomic
    def participar_convocatoria(convocatoria_id, titulo, alianza, financiado,
                                 unidad_ejecutora, linea_investigacion,
                                 valor_solicitado, doc_proyecto, doc_carta, doc_alianza,
                                 ip_creacion, ejecutor):
        """
        Réplica de ProyectoXConvocatoriaServicioImpl.participarConvocatoria()
        (Thymeleaf). Orquestador delgado que encadena servicios ya existentes,
        cada uno de un solo responsabilidad, dentro de UNA sola transacción
        atómica — mismo patrón que ConvocatoriaService.crear_con_documento().
        Secuencia (fiel al original):
          1. Resolver el Gerente vigente (el original no lo pedía en el
             formulario; el nuevo esquema exige gerente NOT NULL en Proyecto).
          2. Crear el Proyecto (siempre interno=True: solo FACULTAD/GRUPO
             postulan a convocatorias internas).
          3. Crear el Monto SIEMPRE (igual que el original: si no hay
             valor_solicitado, se crea con solicitado=0, no se omite).
          4. Registrar hasta 3 documentos (docProyecto obligatorio,
             docCarta y docAlianza opcionales) vía el punto de entrada único
             DocumentoFirmaService.crear_desde_archivo().
          5. Vincular el Proyecto a la Convocatoria (reutiliza
             ProyectoXConvocatoriaService.crear(), que ya valida que la
             convocatoria esté activa y que no exista un vínculo duplicado).
          6. Crear una Calificacion por cada TipoCalificacion (fase) activa,
             igual que el bucle sobre tipoCalificacionRepositorio.findAll().
        """
        from apps.investigacion_formal.services.proyecto_service import ProyectoService
        DOCUMENTOS_QUE_YA_VIENEN_FIRMADOS = {"Propuesta del proyecto", "Carta de Compromiso", "Documento de Alianza"}
        if not doc_proyecto:
            raise ValidationError(
                {"doc_proyecto": "El documento del proyecto es obligatorio para participar en la convocatoria."}
            )
        gerente = GerenteSelector.obtener_actual()
        if gerente is None:
            raise ValidationError(
                "No hay un Gerente vigente registrado en el sistema; no es posible "
                "asignar responsable al proyecto."
            )
        proyecto = ProyectoService.crear(
            usuario_id=ejecutor.pk,
            gerente_id=gerente.pk,
            titulo=titulo,
            interno=True,
            alianza=bool(alianza),
            financiado=bool(financiado),
            unidad_ejecutora=unidad_ejecutora,
            linea_investigacion=linea_investigacion,
            ejecutor=ejecutor,
        )
        MontoService.crear(
            proyecto_id=proyecto.pk,
            solicitado=valor_solicitado or 0,
            ejecutor=ejecutor,
        )
        documentos_a_crear = [
            ("Propuesta del proyecto", doc_proyecto),
            ("Carta de Compromiso", doc_carta),
            ("Documento de Alianza", doc_alianza),
        ]
        for nombre_tipo, archivo in documentos_a_crear:
            if not archivo:
                continue
            tipo_documento = TipoDocumentoSelector.obtener_por_nombre(nombre_tipo)
            if tipo_documento is None:
                raise ValidationError(
                    f"No existe el TipoDocumento '{nombre_tipo}' "
                    f"(seed pendiente: grupo='proyecto', nombre_documento='{nombre_tipo}')."
                )
            DocumentoFirmaService.crear_desde_archivo(
                tipo_documento_id=tipo_documento.pk,
                archivo=archivo,
                ip_creacion=ip_creacion,
                ejecutor=ejecutor,
                objeto=proyecto,
                estado='FIRMADO' if nombre_tipo in DOCUMENTOS_QUE_YA_VIENEN_FIRMADOS else 'BORRADOR',
                carpeta='proyectos',
            )
        vinculo = ProyectoXConvocatoriaService.crear(
            convocatoria_id=convocatoria_id,
            proyecto_id=proyecto.pk,
            ejecutor=ejecutor,
        )
        for tipo_calificacion in TipoCalificacionSelector.listar():
            CalificacionService.crear(
                fase_id=tipo_calificacion.pk,
                aplicar_id=vinculo.pk,
                ejecutor=ejecutor,
            )
        return vinculo