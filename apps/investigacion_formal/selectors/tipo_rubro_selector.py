from apps.investigacion_formal.models import TipoRubro


class TipoRubroSelector:

    @staticmethod
    def listar():
        return TipoRubro.objects.all().order_by('nombre_rubro')

    @staticmethod
    def obtener(tipo_rubro_id):
        return TipoRubro.objects.get(pk=tipo_rubro_id)

    @staticmethod
    def existe(tipo_rubro_id):
        return TipoRubro.objects.filter(pk=tipo_rubro_id).exists()

    @staticmethod
    def existe_nombre(nombre_rubro, excluir_id=None):
        qs = TipoRubro.objects.filter(nombre_rubro__iexact=nombre_rubro)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()
    
    @staticmethod
    def listar_aplicables():
        return TipoRubro.objects.filter(aplica=True).order_by('nombre_rubro')