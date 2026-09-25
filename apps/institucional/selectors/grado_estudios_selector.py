"""
Selector de GradoEstudios.

Interfaz estándar definitiva: listar(), obtener(id) [lanza excepción],
buscar(id) [devuelve None], obtener_por_<campo>(), existe_<campo>().
"""
from apps.institucional.models import GradoEstudios


class GradoEstudiosSelector:

    @staticmethod
    def listar():
        return GradoEstudios.objects.all().order_by('sigla_grado')

    @staticmethod
    def obtener(grado_id):
        return GradoEstudios.objects.get(pk=grado_id)

    @staticmethod
    def buscar(grado_id):
        return GradoEstudios.objects.filter(pk=grado_id).first()

    @staticmethod
    def existe_sigla(sigla_grado, excluir_id=None):
        qs = GradoEstudios.objects.filter(sigla_grado__iexact=sigla_grado)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()