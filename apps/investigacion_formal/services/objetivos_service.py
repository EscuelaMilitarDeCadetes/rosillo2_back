from django.db import transaction

from apps.investigacion_formal.models import Objetivos
from apps.investigacion_formal.selectors.objetivos_selector import ObjetivosSelector
from apps.investigacion_formal.services.proyecto_setup_service import ProyectoSetupService
from apps.investigacion_formal.validators.objetivos_validator import ObjetivosValidator
from apps.common.services.historial_service import HistorialService


class ObjetivosService:

    @staticmethod
    def listar():
        return ObjetivosSelector.listar()

    @staticmethod
    def obtener(objetivo_id):
        return ObjetivosSelector.obtener(objetivo_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        return ObjetivosSelector.listar_por_proyecto(proyecto_id, solo_activos=solo_activos)

    @staticmethod
    def obtener_objetivo_general(proyecto_id):
        return ObjetivosSelector.obtener_objetivo_general_por_proyecto(proyecto_id)

    @staticmethod
    @transaction.atomic
    def crear_objetivo_general(proyecto_id, objetivo, ejecutor):
        """Réplica de agregarObjetivoPrincipal: solo puede existir un objetivo
        general (clase='PRINCIPAL') por proyecto."""
        ObjetivosValidator.validar_creacion(proyecto_id, objetivo, 'PRINCIPAL')
        creado = Objetivos.objects.create(
            proyecto_id=proyecto_id,
            objetivo=objetivo.strip(),
            clase='PRINCIPAL',
            estado=True,
        )
        ProyectoSetupService.verificar_configuracion_completa(proyecto_id, ejecutor=ejecutor)
        HistorialService.registrar(
            ejecutor,
            f"Se creó el objetivo general del proyecto '{creado.proyecto.titulo}' "
            f"(id={creado.pk}).",
            objeto=creado,
        )
        return creado

    @staticmethod
    @transaction.atomic
    def crear_objetivo_especifico(proyecto_id, objetivo, ejecutor):
        ObjetivosValidator.validar_creacion(proyecto_id, objetivo, 'ESPECIFICO')
        creado = Objetivos.objects.create(
            proyecto_id=proyecto_id,
            objetivo=objetivo.strip(),
            clase='ESPECIFICO',
            estado=True,
        )
        ProyectoSetupService.verificar_configuracion_completa(proyecto_id, ejecutor=ejecutor)
        HistorialService.registrar(
            ejecutor,
            f"Se creó el objetivo específico '{creado.objetivo}' del proyecto "
            f"'{creado.proyecto.titulo}' (id={creado.pk}).",
            objeto=creado,
        )
        return creado

    @staticmethod
    @transaction.atomic
    def actualizar(objetivo_id, objetivo, ejecutor):
        registro = ObjetivosSelector.obtener(objetivo_id)
        ObjetivosValidator.validar_actualizacion(
            objetivo_id, registro.proyecto_id, objetivo, registro.clase
        )
        registro.objetivo = objetivo.strip()
        registro.save(update_fields=['objetivo'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó el objetivo '{registro.objetivo}' del proyecto "
            f"'{registro.proyecto.titulo}' (id={registro.pk}).",
            objeto=registro,
        )
        return registro

    @staticmethod
    @transaction.atomic
    def eliminar(objetivo_id, ejecutor):
        registro = ObjetivosSelector.obtener(objetivo_id)
        ObjetivosValidator.validar_eliminacion(registro)
        registro.estado = False
        registro.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se desactivó el objetivo '{registro.objetivo}' del proyecto "
            f"'{registro.proyecto.titulo}' (id={registro.pk}).",
            objeto=registro,
        )
        return registro