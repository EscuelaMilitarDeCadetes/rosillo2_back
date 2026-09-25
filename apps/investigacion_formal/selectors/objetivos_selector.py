from apps.investigacion_formal.models import Objetivos


class ObjetivosSelector:

    @staticmethod
    def listar():
        return Objetivos.objects.select_related('proyecto').all()

    @staticmethod
    def obtener(objetivo_id):
        return Objetivos.objects.select_related('proyecto').get(pk=objetivo_id)

    @staticmethod
    def existe(objetivo_id):
        return Objetivos.objects.filter(pk=objetivo_id).exists()

    @staticmethod
    def existe_texto(objetivo, excluir_id=None):
        qs = Objetivos.objects.filter(objetivo__iexact=objetivo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def obtener_objetivo_general_por_proyecto(proyecto_id):
        return Objetivos.objects.filter(
            proyecto_id=proyecto_id, clase='PRINCIPAL', estado=True
        ).first()

    @staticmethod
    def existe_objetivo_general(proyecto_id):
        return Objetivos.objects.filter(
            proyecto_id=proyecto_id, clase='PRINCIPAL', estado=True
        ).exists()

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        qs = Objetivos.objects.filter(proyecto_id=proyecto_id)
        if solo_activos:
            qs = qs.filter(estado=True)
        return qs