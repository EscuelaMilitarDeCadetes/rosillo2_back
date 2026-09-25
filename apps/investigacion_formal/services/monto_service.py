from django.db import transaction

from apps.investigacion_formal.models import Monto
from apps.investigacion_formal.selectors.monto_selector import MontoSelector
from apps.investigacion_formal.validators.monto_validator import MontoValidator
from apps.common.services.historial_service import HistorialService


class MontoService:

    @staticmethod
    def listar():
        return MontoSelector.listar()

    @staticmethod
    def obtener(monto_id):
        return MontoSelector.obtener(monto_id)

    @staticmethod
    def obtener_por_proyecto(proyecto_id):
        return MontoSelector.obtener_por_proyecto(proyecto_id)

    @staticmethod
    def listar_aprobados_proyectos_calificados(interno=True):
        return MontoSelector.listar_aprobados_proyectos_calificados(interno=interno)

    @staticmethod
    def listar_contrapartida_proyectos_calificados(interno=True):
        return MontoSelector.listar_contrapartida_proyectos_calificados(interno=interno)

    @staticmethod
    def listar_totales_proyectos_calificados(interno=True):
        return MontoSelector.listar_totales_proyectos_calificados(interno=interno)

    @staticmethod
    @transaction.atomic
    def crear(proyecto_id, solicitado, ejecutor):
        """Creado por CINTERNO/CEXTERNO al momento de postular o registrar un
        proyecto financiado."""
        MontoValidator.validar_creacion(proyecto_id, solicitado)
        monto = Monto.objects.create(
            proyecto_id=proyecto_id,
            solicitado=solicitado,
            aprobado=0,
            ejecutado=0,
            contrapartida=0,
            total=0,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró el monto solicitado ({solicitado}) para el proyecto "
            f"'{monto.proyecto.titulo}' (id={monto.pk}).",
            objeto=monto,
        )
        return monto

    @staticmethod
    @transaction.atomic
    def asignar_aprobado(monto_id, aprobado, contrapartida, ejecutor):
        """Réplica de MontoServicio.updateMontoXId: asigna el monto aprobado y la
        contrapartida, y recalcula el total. Exclusivo de CINTERNO/CEXTERNO."""
        from django.utils import timezone
        monto = MontoSelector.obtener(monto_id)
        MontoValidator.validar_asignacion(aprobado, contrapartida)
        monto.aprobado = aprobado
        monto.contrapartida = contrapartida
        monto.total = aprobado + contrapartida
        monto.asignado = timezone.now().date()
        monto.save(update_fields=['aprobado', 'contrapartida', 'total', 'asignado'])
        HistorialService.registrar(
            ejecutor,
            f"Se asignó el monto aprobado ({aprobado}) y contrapartida "
            f"({contrapartida}) al proyecto '{monto.proyecto.titulo}' "
            f"(id={monto.pk}).",
            objeto=monto,
        )
        return monto

    @staticmethod
    @transaction.atomic
    def editar_valor_aprobado(monto_id, nuevo_aprobado, ejecutor):
        """Réplica de MontoServicio.editarMontoXProyecto: modifica el aprobado.
        CORREGIDO: además de 'aprobado', recalcula 'total' con la
        contrapartida ya existente (total = nuevo_aprobado + contrapartida).
        Antes solo se actualizaba 'aprobado' y 'total' quedaba con el valor
        calculado en la asignación inicial (asignar_aprobado), desincronizado
        de cualquier edición posterior. 'total' se usa en ExportacionService
        para reportes, así que debe reflejar siempre aprobado+contrapartida.
        """
        monto = MontoSelector.obtener(monto_id)
        MontoValidator.validar_edicion_gasto(monto, nuevo_aprobado)
        monto.aprobado = nuevo_aprobado
        monto.total = nuevo_aprobado + (monto.contrapartida or 0)
        monto.save(update_fields=['aprobado', 'total'])
        HistorialService.registrar(
            ejecutor,
            f"Se modificó el valor aprobado del proyecto "
            f"'{monto.proyecto.titulo}' a {nuevo_aprobado} (id={monto.pk}).",
            objeto=monto,
        )
        return monto
    
    @staticmethod
    def calcular_avance_presupuestal(proyecto_id):
        return MontoSelector.obtener_avance_presupuestal(proyecto_id)
    
    @staticmethod
    @transaction.atomic
    def asignar_contrapartida(monto_id, contrapartida, ejecutor):
        """Asigna/edita solo la contrapartida y recalcula el total."""
        monto = MontoSelector.obtener(monto_id)
        MontoValidator.validar_contrapartida(contrapartida)
        monto.contrapartida = float(contrapartida)
        monto.total = (monto.aprobado or 0) + monto.contrapartida
        monto.save(update_fields=['contrapartida', 'total'])
        HistorialService.registrar(
            ejecutor,
            f"Se asignó la contrapartida ({monto.contrapartida}) al proyecto "
            f"'{monto.proyecto.titulo}' (id={monto.pk}).",
            objeto=monto,
        )
        return monto