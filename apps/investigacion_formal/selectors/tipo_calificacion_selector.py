from apps.investigacion_formal.models import TipoCalificacion


class TipoCalificacionSelector:

    @staticmethod
    def listar():
        return TipoCalificacion.objects.all().order_by('orden_fase')

    @staticmethod
    def obtener(tipo_calificacion_id):
        return TipoCalificacion.objects.get(pk=tipo_calificacion_id)

    @staticmethod
    def existe(tipo_calificacion_id):
        return TipoCalificacion.objects.filter(pk=tipo_calificacion_id).exists()

    @staticmethod
    def existe_nombre(tipo_calificacion, excluir_id=None):
        qs = TipoCalificacion.objects.filter(tipo_calificacion__iexact=tipo_calificacion)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_evaluables():
        return TipoCalificacion.objects.filter(evaluacion=True).order_by('orden_fase')

    @staticmethod
    def existe_orden(orden_fase, excluir_id=None):
        qs = TipoCalificacion.objects.filter(orden_fase=orden_fase)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()