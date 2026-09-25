from django.db import transaction

from apps.investigacion_formativa.models import BancoIdeas
from apps.investigacion_formativa.selectors.banco_ideas_selector import BancoIdeasSelector
from apps.investigacion_formativa.validators.banco_ideas_validator import BancoIdeasValidator
from apps.common.services.historial_service import HistorialService
from apps.investigacion_formativa.services._soporte import (
    validar_ejecutor_autor_o_gestor,
    persona_actual_de_usuario,
)


class BancoIdeasService:

    @staticmethod
    def listar():
        return BancoIdeasSelector.listar()

    @staticmethod
    def obtener(idea_id):
        return BancoIdeasSelector.obtener(idea_id)
    
    @staticmethod
    def listar_disponibles_por_facultad(facultad_id):
        return BancoIdeasSelector.listar_disponibles_por_facultad(facultad_id)
    
    @staticmethod
    def listar_por_facultad(facultad_id, estado=None):
        return BancoIdeasSelector.listar_por_facultad(facultad_id, estado=estado)

    @staticmethod
    def listar_disponibles(facultad_id=None):
        return BancoIdeasSelector.listar_disponibles(facultad_id=facultad_id)

    @staticmethod
    @transaction.atomic
    def crear(facultad_id, idea, descripcion, linea_investigacion, palabras_clave, ejecutor):
        BancoIdeasValidator.validar_creacion(
            facultad_id, idea, descripcion, linea_investigacion, palabras_clave
        )
        banco_idea = BancoIdeas.objects.create(
            facultad_id=facultad_id,
            idea=idea,
            descripcion=descripcion,
            linea_investigacion=linea_investigacion,
            palabras_clave=palabras_clave,
            estado='DISPONIBLE',
        )
        HistorialService.registrar(
            ejecutor,
            f"Se registró la idea '{banco_idea.idea}' en el banco de ideas de "
            f"'{banco_idea.facultad.nombre_facultad}' (id={banco_idea.pk}).",
            objeto=banco_idea,
        )
        return banco_idea

    @staticmethod
    @transaction.atomic
    def actualizar(idea_id, descripcion, linea_investigacion, palabras_clave, ejecutor):
        banco_idea = BancoIdeasSelector.obtener(idea_id)
        BancoIdeasValidator.validar_actualizacion(
            banco_idea, descripcion, linea_investigacion, palabras_clave
        )
        banco_idea.descripcion = descripcion
        banco_idea.linea_investigacion = linea_investigacion
        banco_idea.palabras_clave = palabras_clave
        banco_idea.save(update_fields=['descripcion', 'linea_investigacion', 'palabras_clave'])
        HistorialService.registrar(
            ejecutor,
            f"Se actualizó la idea '{banco_idea.idea}' (id={banco_idea.pk}).",
            objeto=banco_idea,
        )
        return banco_idea

    @staticmethod
    @transaction.atomic
    def separar(idea_id, ejecutor):
        banco_idea = BancoIdeasSelector.obtener(idea_id)
        BancoIdeasValidator.validar_separacion(banco_idea)
        persona = persona_actual_de_usuario(ejecutor)
        banco_idea.estado = 'SEPARADA'
        banco_idea.separada_por = persona
        banco_idea.save(update_fields=['estado', 'separada_por'])
        HistorialService.registrar(
            ejecutor,
            f"Se separó la idea '{banco_idea.idea}' (id={banco_idea.pk}).",
            objeto=banco_idea,
        )
        return banco_idea
    
    @staticmethod
    @transaction.atomic
    def tomar(idea_id, ejecutor):
        """Confirma la toma de la idea (se invoca típicamente desde
        PostulacionProcesoService/ProcesoFormativoService al aprobar una
        postulación cuyo proceso se origina en esta idea). Si la idea ya
        estaba SEPARADA, solo quien la separó (o un gestor administrativo)
        puede confirmarla como TOMADA; si estaba DISPONIBLE, cualquier
        estudiante habilitado puede tomarla directamente."""
        banco_idea = BancoIdeasSelector.obtener(idea_id)
        if banco_idea.estado == 'SEPARADA' and banco_idea.separada_por_id is not None:
            validar_ejecutor_autor_o_gestor(
                banco_idea.separada_por_id, ejecutor, "esta idea del banco"
            )
        BancoIdeasValidator.validar_toma(banco_idea)
        persona = persona_actual_de_usuario(ejecutor)
        banco_idea.estado = 'TOMADA'
        if persona is not None:
            banco_idea.separada_por = persona
        banco_idea.save(update_fields=['estado', 'separada_por'])
        HistorialService.registrar(
            ejecutor,
            f"La idea '{banco_idea.idea}' fue tomada (id={banco_idea.pk}).",
            objeto=banco_idea,
        )
        return banco_idea

    @staticmethod
    @transaction.atomic
    def liberar(idea_id, ejecutor):
        banco_idea = BancoIdeasSelector.obtener(idea_id)
        # Solo quien la separó puede liberarla voluntariamente; Facultad/Decano/
        # Soporte pueden hacerlo en su nombre (p. ej. si el estudiante abandonó el proceso).
        if banco_idea.separada_por_id is not None:
            validar_ejecutor_autor_o_gestor(
                banco_idea.separada_por_id, ejecutor, "esta idea del banco"
            )
        BancoIdeasValidator.validar_liberacion(banco_idea)
        banco_idea.estado = 'DISPONIBLE'
        banco_idea.separada_por = None
        banco_idea.save(update_fields=['estado', 'separada_por'])
        HistorialService.registrar(
            ejecutor,
            f"Se liberó la idea '{banco_idea.idea}' de vuelta al banco (id={banco_idea.pk}).",
            objeto=banco_idea,
        )
        return banco_idea

    @staticmethod
    @transaction.atomic
    def eliminar(idea_id, ejecutor):
        banco_idea = BancoIdeasSelector.obtener(idea_id)
        BancoIdeasValidator.validar_eliminacion(banco_idea)
        banco_idea.estado = 'ELIMINADA'
        banco_idea.save(update_fields=['estado'])
        HistorialService.registrar(
            ejecutor,
            f"Se eliminó la idea '{banco_idea.idea}' del banco de ideas (id={banco_idea.pk}).",
            objeto=banco_idea,
        )
        return banco_idea