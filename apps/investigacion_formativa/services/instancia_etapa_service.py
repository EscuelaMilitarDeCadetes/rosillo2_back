from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.investigacion_formativa.models import InstanciaEtapa
from apps.investigacion_formativa.selectors.instancia_etapa_selector import InstanciaEtapaSelector
from apps.investigacion_formativa.validators.instancia_etapa_validator import (
    InstanciaEtapaValidator,
)
from apps.investigacion_formativa.services._soporte import ejecutor_autorizado_para_etapa
from apps.common.services.historial_service import HistorialService
from apps.investigacion_formativa.services.avance_service import AvanceService


class InstanciaEtapaService:

    @staticmethod
    def listar():
        return InstanciaEtapaSelector.listar()

    @staticmethod
    def obtener(instancia_id):
        return InstanciaEtapaSelector.obtener(instancia_id)

    @staticmethod
    def listar_por_proceso(proceso_id):
        return InstanciaEtapaSelector.listar_por_proceso(proceso_id)

    @staticmethod
    def _validar_ejecutor_responsable(instancia, ejecutor):
        """Verifica que `ejecutor` sea realmente quien puede resolver esta
        etapa segun EtapaFlujo.rol_responsable (ESTUDIANTE/TUTOR/JURADO/
        FACULTAD, o Decano/Soporte como administradores del flujo).

        Este chequeo es indispensable ademas del permiso de vista: el
        permiso de vista (ver InstanciaEtapaViewSet.get_permissions) solo
        filtra quienes PODRIAN llegar a ser responsables de alguna etapa;
        aqui se valida el caso concreto de ESTA instancia."""
        if not ejecutor_autorizado_para_etapa(instancia, ejecutor):
            raise PermissionDenied(
                "No tiene el rol responsable de esta etapa "
                f"('{instancia.etapa.get_rol_responsable_display()}') para realizar esta accion."
            )

    @staticmethod
    @transaction.atomic
    def crear(proceso_id, etapa_id, ejecutor):
        """Crea el registro de una nueva etapa por la que atraviesa el proceso,
        en estado 'PENDIENTE'. El avance real (iniciar/aprobar/rechazar) es
        responsabilidad de los metodos de negocio de abajo."""
        InstanciaEtapaValidator.validar_creacion(proceso_id, etapa_id)
        instancia = InstanciaEtapa.objects.create(
            proceso_id=proceso_id,
            etapa_id=etapa_id,
            estado='PENDIENTE',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se creó la instancia de la etapa '{instancia.etapa.nombre}' para el proceso "
            f"'{instancia.proceso.titulo}' (id={instancia.pk}).",
            objeto=instancia,
        )
        return instancia

    @staticmethod
    @transaction.atomic
    def iniciar(instancia_id, ejecutor):
        instancia = InstanciaEtapaSelector.obtener(instancia_id)
        InstanciaEtapaService._validar_ejecutor_responsable(instancia, ejecutor)
        InstanciaEtapaValidator.validar_inicio(instancia)
        instancia.estado = 'EN_PROCESO'
        instancia.fecha_inicio = timezone.now()
        instancia.save(update_fields=['estado', 'fecha_inicio'])
        HistorialService.registrar(
            ejecutor,
            f"Se inició la etapa '{instancia.etapa.nombre}' del proceso "
            f"'{instancia.proceso.titulo}' (id={instancia.pk}).",
            objeto=instancia,
        )
        return instancia

    @staticmethod
    @transaction.atomic
    def aprobar(instancia_id, ejecutor):
        instancia = InstanciaEtapaSelector.obtener(instancia_id)
        InstanciaEtapaService._validar_ejecutor_responsable(instancia, ejecutor)
        InstanciaEtapaValidator.validar_aprobacion(instancia)
        instancia.estado = 'APROBADO'
        instancia.fecha_fin = timezone.now()
        instancia.save(update_fields=['estado', 'fecha_fin'])
        # Mantiene ProcesoFormativo.porcentaje_avance sincronizado con cada
        # etapa aprobada, en vez de depender de que alguien lo recalcule
        # manualmente.
        AvanceService.actualizar_porcentaje_avance(instancia.proceso_id, ejecutor=ejecutor)
        HistorialService.registrar(
            ejecutor,
            f"Se aprobó la etapa '{instancia.etapa.nombre}' del proceso "
            f"'{instancia.proceso.titulo}' (id={instancia.pk}).",
            objeto=instancia,
        )
        return instancia

    @staticmethod
    @transaction.atomic
    def rechazar(instancia_id, ejecutor):
        instancia = InstanciaEtapaSelector.obtener(instancia_id)
        InstanciaEtapaService._validar_ejecutor_responsable(instancia, ejecutor)
        InstanciaEtapaValidator.validar_rechazo(instancia)
        instancia.estado = 'RECHAZADO'
        instancia.fecha_fin = timezone.now()
        instancia.save(update_fields=['estado', 'fecha_fin'])
        HistorialService.registrar(
            ejecutor,
            f"Se rechazó la etapa '{instancia.etapa.nombre}' del proceso "
            f"'{instancia.proceso.titulo}' (id={instancia.pk}).",
            objeto=instancia,
        )
        return instancia

    @staticmethod
    @transaction.atomic
    def marcar_segunda_instancia(instancia_id, ejecutor):
        instancia = InstanciaEtapaSelector.obtener(instancia_id)
        InstanciaEtapaService._validar_ejecutor_responsable(instancia, ejecutor)
        InstanciaEtapaValidator.validar_paso_a_segunda_instancia(instancia)
        instancia.estado = 'SEGUNDA_INSTANCIA'
        instancia.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"La etapa '{instancia.etapa.nombre}' del proceso '{instancia.proceso.titulo}' "
            f"pasó a segunda instancia (id={instancia.pk}).",
            objeto=instancia,
        )
        return instancia