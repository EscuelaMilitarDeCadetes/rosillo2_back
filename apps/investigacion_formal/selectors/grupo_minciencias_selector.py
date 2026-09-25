from apps.investigacion_formal.models import GrupoMinciencias


class GrupoMincienciasSelector:

    @staticmethod
    def listar():
        return GrupoMinciencias.objects.all().order_by('nombre_grupo_minciencias')

    @staticmethod
    def obtener(grupo_minciencias_id):
        return GrupoMinciencias.objects.get(pk=grupo_minciencias_id)

    @staticmethod
    def existe(grupo_minciencias_id):
        return GrupoMinciencias.objects.filter(pk=grupo_minciencias_id).exists()

    @staticmethod
    def existe_nombre(nombre_grupo_minciencias, excluir_id=None):
        qs = GrupoMinciencias.objects.filter(
            nombre_grupo_minciencias__iexact=nombre_grupo_minciencias
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()