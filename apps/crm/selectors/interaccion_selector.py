from apps.crm.models import Interaccion


class InteraccionSelector:

    @staticmethod
    def listar():
        return Interaccion.objects.select_related('entidad', 'proyecto_asociado').all()

    @staticmethod
    def obtener(interaccion_id):
        return (
            Interaccion.objects
            .select_related('entidad', 'proyecto_asociado')
            .get(pk=interaccion_id)
        )

    @staticmethod
    def listar_por_entidad(entidad_id):
        return (
            Interaccion.objects
            .select_related('proyecto_asociado')
            .filter(entidad_id=entidad_id)
            .order_by('-fecha')
        )

    @staticmethod
    def listar_por_proyecto(proyecto_id):
        return (
            Interaccion.objects
            .select_related('entidad')
            .filter(proyecto_asociado_id=proyecto_id)
            .order_by('-fecha')
        )

    @staticmethod
    def listar_por_medio(medio):
        return (
            Interaccion.objects
            .select_related('entidad', 'proyecto_asociado')
            .filter(medio=medio)
            .order_by('-fecha')
        )