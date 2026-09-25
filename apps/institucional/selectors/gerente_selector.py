"""
Selector de Gerente.

Entidad nueva (sin precedente en Thymeleaf). Interfaz estándar definitiva
más las consultas especializadas que la regla de negocio exige.
"""
from apps.institucional.models import Gerente


class GerenteSelector:

    @staticmethod
    def listar():
        """
        Devuelve solo los registros vigentes (estado=True). Dado que la
        regla de negocio garantiza máximo un Gerente activo a la vez,
        esto en la práctica devuelve 0 o 1 elemento — pero se mantiene
        como queryset por consistencia con la interfaz estándar 'listar()'.
        """
        return (
            Gerente.objects
            .select_related('persona')
            .filter(estado=True)
            .order_by('-fecha_ingreso')
        )
        
    @staticmethod
    def listar_historico():
        """
        Devuelve TODOS los registros (activos, finalizados y soft-deleted).
        Es el listado completo histórico, separado de listar() para no
        mezclar "vigentes" con "todos" bajo el mismo nombre de método.
        """
        return Gerente.objects.select_related('persona').all().order_by('-fecha_ingreso')

    @staticmethod
    def obtener(gerente_id):
        return Gerente.objects.select_related('persona').get(pk=gerente_id)

    @staticmethod
    def obtener_actual():
        """
        Devuelve el Gerente vigente: estado=True y sin fecha_salida.
        """
        return (
            Gerente.objects
            .select_related('persona')
            .filter(estado=True, fecha_salida__isnull=True)
            .order_by('-fecha_ingreso')
            .first()
        )

    @staticmethod
    def existe_activo_distinto_de(excluir_id=None):
        """
        Soporta la regla: solo puede existir un Gerente activo a la vez.
        """
        qs = Gerente.objects.filter(estado=True, fecha_salida__isnull=True)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()