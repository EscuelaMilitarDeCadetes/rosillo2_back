from apps.investigacion_formativa.models import BancoIdeas


class BancoIdeasSelector:

    @staticmethod
    def listar():
        return (
            BancoIdeas.objects
            .select_related('facultad')
            .order_by('-fecha_creacion')
        )

    @staticmethod
    def obtener(idea_id):
        return BancoIdeas.objects.get(pk=idea_id)

    @staticmethod
    def existe_idea_en_facultad(facultad_id, idea, excluir_id=None):
        """Valida unique_together ('facultad', 'idea') antes de crear/actualizar.
        Los títulos de las ideas deben ser únicos por facultad; las áreas/líneas sí se pueden repetir."""
        qs = BancoIdeas.objects.filter(facultad_id=facultad_id, idea__iexact=idea)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_por_facultad(facultad_id, estado=None):
        qs = BancoIdeas.objects.filter(facultad_id=facultad_id)
        if estado is not None:
            qs = qs.filter(estado=estado)
        return qs.order_by('-fecha_creacion')

    @staticmethod
    def listar_disponibles(facultad_id=None):
        qs = BancoIdeas.objects.filter(estado='DISPONIBLE')
        if facultad_id is not None:
            qs = qs.filter(facultad_id=facultad_id)
        return qs.select_related('facultad').order_by('-fecha_creacion')
    
    @staticmethod
    def listar_disponibles_por_facultad(facultad_id):
        return BancoIdeasSelector.listar_disponibles(facultad_id=facultad_id)