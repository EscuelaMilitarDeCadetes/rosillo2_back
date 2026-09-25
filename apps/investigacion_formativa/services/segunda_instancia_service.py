from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.investigacion_formativa.models import SegundaInstancia
from apps.investigacion_formativa.selectors.segunda_instancia_selector import (
    SegundaInstanciaSelector,
)
from apps.investigacion_formativa.validators.segunda_instancia_validator import (
    SegundaInstanciaValidator,
)
from apps.investigacion_formativa.services._soporte import (
    notificar,
    usuario_id_estudiante_de_proceso,
    usuarios_ids_participantes_de_proceso,
)
from apps.common.services.historial_service import HistorialService
from apps.common.services.aprobacion_service import AprobacionService
from apps.common.selectors.aprobacion_selector import AprobacionSelector
from apps.common.selectors.tipo_documento_selector import TipoDocumentoSelector

TIPO_DOCUMENTO_APROBACION_SEGUNDA_INSTANCIA = 'APROBACION_SEGUNDA_INSTANCIA'


class SegundaInstanciaService:

    @staticmethod
    def listar():
        return SegundaInstanciaSelector.listar()

    @staticmethod
    def obtener(segunda_instancia_id):
        return SegundaInstanciaSelector.obtener(segunda_instancia_id)

    @staticmethod
    def listar_activadas_pendientes():
        return SegundaInstanciaSelector.listar_activadas_pendientes()

    @staticmethod
    @transaction.atomic
    def crear(proceso_id, instancia_etapa_id, evaluacion_id, etapa_retorno_id,
              tipo, motivo, ejecutor, nota_maxima=3.5):
        SegundaInstanciaValidator.validar_creacion(
            proceso_id, instancia_etapa_id, evaluacion_id, etapa_retorno_id,
            tipo, motivo, nota_maxima,
        )
        segunda_instancia = SegundaInstancia.objects.create(
            proceso_id=proceso_id,
            instancia_etapa_id=instancia_etapa_id,
            evaluacion_id=evaluacion_id,
            etapa_retorno_id=etapa_retorno_id,
            tipo=tipo,
            motivo=motivo,
            nota_maxima=nota_maxima,
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró una segunda instancia de tipo '{tipo}' para el proceso "
            f"'{segunda_instancia.proceso.titulo}' (id={segunda_instancia.pk}).",
            objeto=segunda_instancia,
        )
        return segunda_instancia

    @staticmethod
    @transaction.atomic
    def activar(segunda_instancia_id, ejecutor):
        """Uso directo (Decano/CInterno/Soporte). Si quien decide es Facultad,
        usar `solicitar_activacion_decano()` en su lugar."""
        segunda_instancia = SegundaInstanciaSelector.obtener(segunda_instancia_id)
        SegundaInstanciaValidator.validar_activacion(segunda_instancia)
        segunda_instancia.activada = True
        segunda_instancia.save(update_fields=['activada'])
        HistorialService.registrar(
            ejecutor,
            f"Se activó la segunda instancia (id={segunda_instancia.pk}) del proceso "
            f"'{segunda_instancia.proceso.titulo}'.",
            objeto=segunda_instancia,
        )
        proceso = segunda_instancia.proceso
        notificar(
            usuario_id_estudiante_de_proceso(proceso),
            f"Se activó una segunda instancia de tipo '{segunda_instancia.tipo}' en tu "
            f"proceso '{proceso.titulo}'. Motivo: {segunda_instancia.motivo}",
            tipo='alerta',
        )
        notificar_varios_tutor = usuarios_ids_participantes_de_proceso(proceso, ['TUTOR'])
        for usuario_id in notificar_varios_tutor:
            notificar(
                usuario_id,
                f"Se activó una segunda instancia de tipo '{segunda_instancia.tipo}' en el "
                f"proceso '{proceso.titulo}'.",
                tipo='alerta',
            )
        return segunda_instancia

    @staticmethod
    @transaction.atomic
    def consumir(segunda_instancia_id, ejecutor):
        """Marca la segunda instancia como consumida y refleja el consumo en el
        ProcesoFormativo asociado (segunda_instancia_consumida)."""
        segunda_instancia = SegundaInstanciaSelector.obtener(segunda_instancia_id)
        SegundaInstanciaValidator.validar_consumo(segunda_instancia)
        segunda_instancia.consumida = True
        segunda_instancia.save(update_fields=['consumida'])
        proceso = segunda_instancia.proceso
        proceso.segunda_instancia_consumida = True
        proceso.save(update_fields=['segunda_instancia_consumida'])
        HistorialService.registrar(
            ejecutor,
            f"Se consumió la segunda instancia (id={segunda_instancia.pk}) del proceso "
            f"'{proceso.titulo}'.",
            objeto=segunda_instancia,
        )
        return segunda_instancia
    
    @staticmethod
    @transaction.atomic
    def solicitar_activacion_decano(segunda_instancia_id, usuario_revisor_id, ejecutor, observacion=None):
        """Facultad solicita al Decano que decida sobre la activación de una
        segunda instancia. No cambia 'activada': solo abre una Aprobacion
        pendiente. Usar `confirmar_activacion_decano()` o
        `denegar_activacion_decano()` para resolverla."""
        segunda_instancia = SegundaInstanciaSelector.obtener(segunda_instancia_id)
        SegundaInstanciaValidator.validar_activacion(segunda_instancia)

        if not usuario_revisor_id:
            raise ValidationError(
                {"usuario_revisor_id": "Debe indicar el Decano que revisará la activación."}
            )

        tipo_documento = TipoDocumentoSelector.obtener_por_nombre(
            TIPO_DOCUMENTO_APROBACION_SEGUNDA_INSTANCIA
        )
        aprobacion = AprobacionService.crear(
            usuario_revisor_id=usuario_revisor_id,
            tipo_documento_id=tipo_documento.pk,
            id_documento=segunda_instancia.pk,
            ejecutor=ejecutor,
            observacion=observacion,
        )
        HistorialService.registrar(
            ejecutor,
            f"La activación de la segunda instancia (id={segunda_instancia.pk}) del proceso "
            f"'{segunda_instancia.proceso.titulo}' quedó pendiente de aprobación del Decano "
            f"(aprobacion id={aprobacion.pk}).",
            objeto=segunda_instancia,
        )
        notificar(
            usuario_revisor_id,
            f"Tienes una activación de segunda instancia pendiente de tu aprobación: "
            f"proceso '{segunda_instancia.proceso.titulo}', tipo '{segunda_instancia.tipo}'.",
            tipo='info',
        )
        return aprobacion

    @staticmethod
    @transaction.atomic
    def confirmar_activacion_decano(aprobacion_id, ejecutor, observacion_decano=None):
        """El Decano confirma la solicitud abierta por Facultad: aprueba la
        Aprobacion y aplica el efecto de negocio (activa la segunda instancia,
        como en `activar()`)."""
        aprobacion = AprobacionSelector.obtener(aprobacion_id)
        if aprobacion.tipo_documento.nombre_documento != TIPO_DOCUMENTO_APROBACION_SEGUNDA_INSTANCIA:
            raise ValidationError("La Aprobacion indicada no corresponde a una segunda instancia.")

        AprobacionService.aprobar(aprobacion_id, ejecutor, observacion_decano)
        return SegundaInstanciaService.activar(aprobacion.id_documento, ejecutor)

    @staticmethod
    @transaction.atomic
    def denegar_activacion_decano(aprobacion_id, ejecutor, observacion):
        """El Decano deniega la solicitud abierta por Facultad: rechaza la
        Aprobacion. La segunda instancia queda tal cual (activada=False);
        no hay un 'rechazar()' propio del modelo porque no activar no es un
        estado que requiera revertirse."""
        aprobacion = AprobacionSelector.obtener(aprobacion_id)
        if aprobacion.tipo_documento.nombre_documento != TIPO_DOCUMENTO_APROBACION_SEGUNDA_INSTANCIA:
            raise ValidationError("La Aprobacion indicada no corresponde a una segunda instancia.")

        AprobacionService.rechazar(aprobacion_id, ejecutor, observacion)
        segunda_instancia = SegundaInstanciaSelector.obtener(aprobacion.id_documento)
        HistorialService.registrar(
            ejecutor,
            f"El Decano denegó la activación de la segunda instancia (id={segunda_instancia.pk}) "
            f"del proceso '{segunda_instancia.proceso.titulo}': {observacion}",
            objeto=segunda_instancia,
        )
        notificar(
            usuario_id_estudiante_de_proceso(segunda_instancia.proceso),
            f"La solicitud de segunda instancia en tu proceso "
            f"'{segunda_instancia.proceso.titulo}' fue denegada. Motivo: {observacion}",
            tipo='alerta',
        )
        return segunda_instancia

    @staticmethod
    @transaction.atomic
    def eliminar(segunda_instancia_id, ejecutor):
        segunda_instancia = SegundaInstanciaSelector.obtener(segunda_instancia_id)
        SegundaInstanciaValidator.validar_eliminacion(segunda_instancia)
        segunda_instancia.activa = False
        segunda_instancia.save(update_fields=['activa'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó (soft-delete) la segunda instancia (id={segunda_instancia.pk}) "
            f"del proceso '{segunda_instancia.proceso.titulo}'.",
            objeto=segunda_instancia,
        )
        return segunda_instancia