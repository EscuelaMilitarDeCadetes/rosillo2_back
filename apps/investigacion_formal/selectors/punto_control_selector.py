from apps.investigacion_formal.models import PuntoControl


class PuntoControlSelector:

    @staticmethod
    def listar():
        return PuntoControl.objects.filter(estado=True).order_by('control')

    @staticmethod
    def obtener(punto_control_id):
        return PuntoControl.objects.get(pk=punto_control_id)

    @staticmethod
    def existe(punto_control_id):
        return PuntoControl.objects.filter(pk=punto_control_id).exists()

    @staticmethod
    def obtener_por_control(control):
        return PuntoControl.objects.filter(control__iexact=control).first()

    @staticmethod
    def existe_control(control, excluir_id=None):
        qs = PuntoControl.objects.filter(control__iexact=control)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()