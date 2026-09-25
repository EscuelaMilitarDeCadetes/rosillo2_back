"""
Selector de RolGrupo.

Interfaz estándar definitiva.
"""
from apps.institucional.models import RolGrupo


class RolGrupoSelector:

    @staticmethod
    def listar():
        return RolGrupo.objects.all().order_by('id')

    @staticmethod
    def obtener(rol_grupo_id):
        return RolGrupo.objects.get(pk=rol_grupo_id)

    @staticmethod
    def buscar(rol_grupo_id):
        return RolGrupo.objects.filter(pk=rol_grupo_id).first()

    @staticmethod
    def existe_cargo(cargo, excluir_id=None):
        qs = RolGrupo.objects.filter(cargo__iexact=cargo)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()