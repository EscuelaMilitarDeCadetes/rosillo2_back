from apps.investigacion_formal.models import ControlCambios


class ControlCambiosSelector:

    @staticmethod
    def listar():
        return ControlCambios.objects.select_related('proyecto').all()

    @staticmethod
    def obtener(control_cambios_id):
        return ControlCambios.objects.select_related('proyecto').get(pk=control_cambios_id)

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return (
            ControlCambios.objects
            .filter(proyecto_id=proyecto_id)
            .order_by('-fecha_cambio')
        )