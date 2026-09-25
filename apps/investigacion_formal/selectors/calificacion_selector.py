from apps.investigacion_formal.models import Calificacion


class CalificacionSelector:

    @staticmethod
    def listar():
        return Calificacion.objects.select_related('fase', 'aplicar').all()

    @staticmethod
    def obtener(calificacion_id):
        return Calificacion.objects.select_related('fase', 'aplicar').get(pk=calificacion_id)

    @staticmethod
    def listar_por_proyecto_x_convocatoria(aplicar_id):
        return (
            Calificacion.objects
            .select_related('fase')
            .filter(aplicar_id=aplicar_id)
            .order_by('fase__orden_fase')
        )

    @staticmethod
    def existe_calificacion(fase_id, aplicar_id, excluir_id=None):
        qs = Calificacion.objects.filter(fase_id=fase_id, aplicar_id=aplicar_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def contar_fases_calificadas(aplicar_id):
        return Calificacion.objects.filter(
            aplicar_id=aplicar_id, aprobado=True
        ).count()