from apps.investigacion_formal.models import Monto


class MontoSelector:

    @staticmethod
    def listar():
        return Monto.objects.select_related('proyecto').all()

    @staticmethod
    def obtener(monto_id):
        return Monto.objects.select_related('proyecto').get(pk=monto_id)

    @staticmethod
    def buscar(monto_id):
        return Monto.objects.select_related('proyecto').filter(pk=monto_id).first()

    @staticmethod
    def existe(monto_id):
        return Monto.objects.filter(pk=monto_id).exists()

    @staticmethod
    def obtener_por_proyecto(proyecto_id):
        return Monto.objects.select_related('proyecto').filter(proyecto_id=proyecto_id).first()

    @staticmethod
    def listar_aprobados_proyectos_calificados(interno=True):
        return (
            Monto.objects
            .select_related('proyecto')
            .filter(
                proyecto__estado_aprobado='APROBADO',
                proyecto__interno=interno,
                proyecto__proyectoxconvocatoria__estado_finalizado_calificacion=True,
            )
            .order_by('-aprobado')
            .distinct()
        )

    @staticmethod
    def listar_contrapartida_proyectos_calificados(interno=True):
        return (
            Monto.objects
            .select_related('proyecto')
            .filter(
                proyecto__estado_aprobado='APROBADO',
                proyecto__interno=interno,
                proyecto__proyectoxconvocatoria__estado_finalizado_calificacion=True,
            )
            .order_by('-contrapartida')
            .distinct()
        )

    @staticmethod
    def listar_totales_proyectos_calificados(interno=True):
        return (
            Monto.objects
            .select_related('proyecto')
            .filter(
                proyecto__estado_aprobado='APROBADO',
                proyecto__interno=interno,
                proyecto__proyectoxconvocatoria__estado_finalizado_calificacion=True,
            )
            .order_by('-total')
            .distinct()
        )

    @staticmethod
    def existe_para_proyecto(proyecto_id, excluir_id=None):
        qs = Monto.objects.filter(proyecto_id=proyecto_id)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
    
    @staticmethod
    def obtener_avance_presupuestal(proyecto_id):
        """
        % avance presupuestal = ejecutado acumulado / aprobado.
        Equivalente a H2 = D2/C2 del Excel GINSI.
        """
        monto = MontoSelector.obtener_por_proyecto(proyecto_id)
        if monto is None or not monto.aprobado:
            return 0.0
        ejecutado = monto.ejecutado or 0
        return round((ejecutado / monto.aprobado) * 100, 2)