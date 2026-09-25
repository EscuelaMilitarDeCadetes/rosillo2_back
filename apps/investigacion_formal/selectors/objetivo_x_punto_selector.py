from apps.investigacion_formal.models import ObjetivoXPunto


class ObjetivoXPuntoSelector:

    @staticmethod
    def listar():
        return ObjetivoXPunto.objects.select_related('objetivo', 'punto_control').all()

    @staticmethod
    def obtener(objetivo_x_punto_id):
        return (
            ObjetivoXPunto.objects
            .select_related('objetivo', 'punto_control')
            .get(pk=objetivo_x_punto_id)
        )

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        qs = (
            ObjetivoXPunto.objects
            .select_related('objetivo', 'punto_control')
            .filter(objetivo__proyecto_id=proyecto_id)
        )
        if solo_activos:
            qs = qs.filter(estado=True)
        return qs

    @staticmethod
    def listar_por_objetivo(objetivo_id, solo_activos=True):
        qs = ObjetivoXPunto.objects.select_related('punto_control').filter(objetivo_id=objetivo_id)
        if solo_activos:
            qs = qs.filter(estado=True)
        return qs

    @staticmethod
    def obtener_activo_por_punto_control(punto_control_id):
        return (
            ObjetivoXPunto.objects
            .select_related('objetivo')
            .filter(punto_control_id=punto_control_id, estado=True)
            .first()
        )

    @staticmethod
    def existe_vinculo(objetivo_id, punto_control_id, excluir_id=None):
        qs = ObjetivoXPunto.objects.filter(
            objetivo_id=objetivo_id, punto_control_id=punto_control_id
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()