from apps.crm.models import EntidadExterna


class EntidadExternaSelector:

    @staticmethod
    def listar():
        return EntidadExterna.objects.all().order_by('nombre')

    @staticmethod
    def obtener(entidad_id):
        return EntidadExterna.objects.get(pk=entidad_id)

    @staticmethod
    def existe(entidad_id):
        return EntidadExterna.objects.filter(pk=entidad_id).exists()

    @staticmethod
    def listar_por_tipo_relacion(tipo_relacion):
        return (
            EntidadExterna.objects
            .filter(tipo_relacion=tipo_relacion)
            .order_by('nombre')
        )

    @staticmethod
    def listar_por_sector(sector):
        return EntidadExterna.objects.filter(sector__iexact=sector).order_by('nombre')

    @staticmethod
    def listar_por_pais(pais):
        return EntidadExterna.objects.filter(pais__iexact=pais).order_by('nombre')