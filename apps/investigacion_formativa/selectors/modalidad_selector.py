# apps/investigacion_formativa/selectors/modalidad_selector.py
from apps.investigacion_formativa.models import Modalidad


class ModalidadSelector:

    @staticmethod
    def listar():
        return Modalidad.objects.all().order_by('nombre')

    @staticmethod
    def obtener(modalidad_id):
        return Modalidad.objects.get(pk=modalidad_id)
    
    @staticmethod
    def existe(modalidad_id):
        return Modalidad.objects.filter(pk=modalidad_id).exists()

    @staticmethod
    def listar_activas():
        return Modalidad.objects.filter(activo=True).order_by('nombre')
    
    @staticmethod
    def existe_nombre(nombre, excluir_id=None):
        qs = Modalidad.objects.filter(nombre__iexact=nombre)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
