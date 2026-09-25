from django.db import transaction
from apps.crm.models import Interaccion
from apps.crm.selectors.interaccion_selector import InteraccionSelector
from apps.crm.validators.interaccion_validator import InteraccionValidator
from apps.common.services.historial_service import HistorialService

_UNSET = object()

class InteraccionService:

    @staticmethod
    def listar():
        return InteraccionSelector.listar()

    @staticmethod
    def obtener(interaccion_id):
        return InteraccionSelector.obtener(interaccion_id)

    @staticmethod
    @transaction.atomic
    def crear(entidad_id, medio, resumen, ejecutor, proyecto_asociado_id=None):
        InteraccionValidator.validar_creacion(entidad_id, medio, resumen, proyecto_asociado_id)
        interaccion = Interaccion.objects.create(
            entidad_id=entidad_id,
            proyecto_asociado_id=proyecto_asociado_id,
            medio=medio,
            resumen=resumen.strip(),
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró una interacción ({interaccion.medio}) con la entidad "
            f"id={entidad_id}"
            + (f", asociada al proyecto id={proyecto_asociado_id}" if proyecto_asociado_id else "")
            + f" (id={interaccion.pk}).",
            objeto=interaccion,
        )
        return interaccion

    @staticmethod
    @transaction.atomic
    def actualizar(interaccion_id, ejecutor, entidad_id=_UNSET, medio=_UNSET, resumen=_UNSET, proyecto_asociado_id=_UNSET):
        interaccion = InteraccionSelector.obtener(interaccion_id)

        nuevo_entidad_id = (entidad_id if entidad_id is not _UNSET else interaccion.entidad_id)
        nuevo_medio = (medio if medio is not _UNSET else interaccion.medio)
        nuevo_resumen = (resumen if resumen is not _UNSET else interaccion.resumen)
        nuevo_proyecto_asociado_id = (proyecto_asociado_id if proyecto_asociado_id is not _UNSET else interaccion.proyecto_asociado_id)

        InteraccionValidator.validar_actualizacion(
            interaccion_id, nuevo_entidad_id, nuevo_medio,
            nuevo_resumen, nuevo_proyecto_asociado_id,
        )

        interaccion.entidad_id = nuevo_entidad_id
        interaccion.medio = nuevo_medio
        interaccion.resumen = nuevo_resumen.strip() if nuevo_resumen is not None else None
        interaccion.proyecto_asociado_id = nuevo_proyecto_asociado_id
        interaccion.save(update_fields=["entidad", "medio", "resumen", "proyecto_asociado"])

        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la interacción id={interaccion.pk} "
            f"(entidad id={interaccion.entidad_id}).",
            objeto=interaccion,
        )
        return interaccion

    @staticmethod
    @transaction.atomic
    def eliminar(interaccion_id, ejecutor):
        interaccion = InteraccionSelector.obtener(interaccion_id)
        InteraccionValidator.validar_eliminacion(interaccion)

        descripcion = (
            f"Se eliminó la interacción id={interaccion.pk} "
            f"(entidad id={interaccion.entidad_id}, medio={interaccion.medio})."
        )
        HistorialService.registrar(ejecutor, descripcion)
        interaccion.delete()
        return True

    @staticmethod
    def listar_por_entidad(entidad_id):
        return InteraccionSelector.listar_por_entidad(entidad_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return InteraccionSelector.listar_por_proyecto(proyecto_id)

    @staticmethod
    def listar_por_medio(medio):
        return InteraccionSelector.listar_por_medio(medio)