from django.db import transaction

from apps.investigacion_formal.models import ObjetivoXPunto, PuntoControl
from apps.investigacion_formal.selectors.objetivo_x_punto_selector import ObjetivoXPuntoSelector
from apps.investigacion_formal.selectors.punto_control_selector import PuntoControlSelector
from apps.investigacion_formal.validators.objetivo_x_punto_validator import ObjetivoXPuntoValidator
from apps.investigacion_formal.validators.punto_control_validator import PuntoControlValidator
from apps.common.services.historial_service import HistorialService


class ObjetivoXPuntoService:

    @staticmethod
    def listar():
        return ObjetivoXPuntoSelector.listar()

    @staticmethod
    def obtener(objetivo_x_punto_id):
        return ObjetivoXPuntoSelector.obtener(objetivo_x_punto_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        return ObjetivoXPuntoSelector.listar_por_proyecto(proyecto_id, solo_activos=solo_activos)

    @staticmethod
    def listar_por_objetivo(objetivo_id, solo_activos=True):
        return ObjetivoXPuntoSelector.listar_por_objetivo(objetivo_id, solo_activos=solo_activos)

    @staticmethod
    @transaction.atomic
    def crear(objetivo_id, control, peso, ejecutor):
        """Réplica de agregarObjetivoXPunto: crea (o reutiliza) el PuntoControl
        por nombre y lo vincula al objetivo con avance inicial en 0."""
        punto_control = PuntoControlSelector.obtener_por_control(control)
        if punto_control is None:
            PuntoControlValidator.validar_creacion(control, peso)
            punto_control = PuntoControl.objects.create(
                control=control.strip(),
                peso=peso,
                completado=0,
                estado=True,
            )

        ObjetivoXPuntoValidator.validar_creacion(
            objetivo_id, punto_control.pk, 'Ninguna', 0, 'ENERO', 1
        )
        vinculo = ObjetivoXPunto.objects.create(
            objetivo_id=objetivo_id,
            punto_control=punto_control,
            descripcion_avance='Ninguna',
            avance=0,
            mes_avance='ENERO',
            anio_avance=1,
            estado=True,
        )

        HistorialService.registrar(
            ejecutor,
            f"Se creó el punto de control '{punto_control.control}' para el "
            f"objetivo '{vinculo.objetivo.objetivo}' del proyecto "
            f"'{vinculo.objetivo.proyecto.titulo}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo

    @staticmethod
    @transaction.atomic
    def agregar_avance(punto_control_id, descripcion_avance, avance, mes_avance, anio_avance, ejecutor):
        ObjetivoXPuntoValidator.validar_nuevo_avance(
            descripcion_avance, avance, mes_avance, anio_avance
        )
        punto_control = PuntoControlSelector.obtener(punto_control_id)
        punto_control.completado = avance
        punto_control.save(update_fields=['completado'])
        vigente = ObjetivoXPuntoSelector.obtener_activo_por_punto_control(punto_control_id)
        if vigente is None:
            raise ValueError(
                f"No existe un ObjetivoXPunto activo para el punto de control "
                f"id={punto_control_id}."
            )
        # NUEVO: distinguir corrección del mismo mes vs. reporte de un mes nuevo,
        # para que quien carga el dato reciba confirmación explícita de cuál
        # de las dos operaciones acaba de ejecutar (mitiga el error silencioso).
        es_correccion_mismo_mes = (
            vigente.mes_avance == mes_avance.strip() and vigente.anio_avance == anio_avance
        )
        vigente.estado = False
        vigente.save(update_fields=['estado'])
        nuevo = ObjetivoXPunto.objects.create(
            objetivo=vigente.objetivo,
            punto_control=punto_control,
            descripcion_avance=descripcion_avance.strip(),
            avance=avance,
            mes_avance=mes_avance.strip(),
            anio_avance=anio_avance,
            estado=True,
        )
        if es_correccion_mismo_mes:
            HistorialService.registrar(
                ejecutor,
                f"Se CORRIGIÓ el avance de {mes_avance}/{anio_avance} ({vigente.avance}% → "
                f"{avance}%) para el objetivo '{nuevo.objetivo.objetivo}' del proyecto "
                f"'{nuevo.objetivo.proyecto.titulo}'.",
                objeto=nuevo,
            )
        else:
            HistorialService.registrar(
                ejecutor,
                f"Se registró un nuevo avance ({avance}%) para el objetivo "
                f"'{nuevo.objetivo.objetivo}' del proyecto '{nuevo.objetivo.proyecto.titulo}'.",
                objeto=nuevo,
            )
        return nuevo, es_correccion_mismo_mes

    @staticmethod
    @transaction.atomic
    def eliminar(objetivo_x_punto_id, ejecutor):
        vinculo = ObjetivoXPuntoSelector.obtener(objetivo_x_punto_id)
        ObjetivoXPuntoValidator.validar_eliminacion(vinculo)
        vinculo.estado = False
        vinculo.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó el avance del punto de control "
            f"'{vinculo.punto_control.control}' (id={vinculo.pk}).",
            objeto=vinculo,
        )
        return vinculo