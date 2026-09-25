from django.db.models import Q
from django.utils import timezone

from apps.investigacion_formativa.models import FlujoProceso


class FlujoProcesoSelector:

    @staticmethod
    def listar():
        return (
            FlujoProceso.objects
            .select_related('modalidad')
            .order_by('modalidad', 'version')
        )

    @staticmethod
    def obtener(flujo_id):
        return FlujoProceso.objects.get(pk=flujo_id)
    
    @staticmethod
    def existe(flujo_id):
        return FlujoProceso.objects.filter(pk=flujo_id).exists()

    @staticmethod
    def existe_nombre(nombre, excluir_id=None):
        qs = FlujoProceso.objects.filter(nombre__iexact=nombre)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def existe_version_en_modalidad(modalidad_id, version, excluir_id=None):
        """Valida unique_together ('modalidad', 'version') antes de crear/actualizar."""
        qs = FlujoProceso.objects.filter(modalidad_id=modalidad_id, version=version)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def listar_por_modalidad(modalidad_id, activo=None):
        qs = FlujoProceso.objects.filter(modalidad_id=modalidad_id)
        if activo is not None:
            qs = qs.filter(activo=activo)
        return qs.order_by('-version')

    @staticmethod
    def obtener_version_vigente(modalidad_id):
        """Versión activa y vigente por fecha para una modalidad — la que debe usarse al iniciar un nuevo ProcesoFormativo."""
        hoy = timezone.now().date()
        return (
            FlujoProceso.objects
            .filter(modalidad_id=modalidad_id, activo=True, fecha_vigencia_inicio__lte=hoy)
            .filter(Q(fecha_vigencia_fin__isnull=True) | Q(fecha_vigencia_fin__gte=hoy))
            .order_by('-version')
            .first()
        )

    @staticmethod
    def listar_activos():
        return FlujoProceso.objects.filter(activo=True).select_related('modalidad')