from django.db.models import Sum

from apps.investigacion_formal.models import Ejecucion


class EjecucionSelector:

    @staticmethod
    def listar():
        return Ejecucion.objects.select_related('monto', 'tipo_rubro').filter(estado=True)

    @staticmethod
    def obtener(ejecucion_id):
        return Ejecucion.objects.select_related('monto', 'tipo_rubro').get(pk=ejecucion_id)

    @staticmethod
    def listar_por_monto(monto_id, solo_activas=True):
        qs = Ejecucion.objects.select_related('tipo_rubro').filter(monto_id=monto_id)
        if solo_activas:
            qs = qs.filter(estado=True)
        return qs