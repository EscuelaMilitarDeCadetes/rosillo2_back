from apps.common.models import TipoDocumento


class TipoDocumentoSelector:
    @staticmethod
    def listar(investigacion=None):
        qs = TipoDocumento.objects.all()
        if investigacion is not None:
            qs = qs.filter(investigacion=investigacion)
        return qs.order_by('nombre_documento')

    @staticmethod
    def obtener(tipo_documento_id):
        return TipoDocumento.objects.get(pk=tipo_documento_id)

    @staticmethod
    def buscar(tipo_documento_id):
        return TipoDocumento.objects.filter(pk=tipo_documento_id).first()

    @staticmethod
    def obtener_por_nombre(nombre_documento):
        return TipoDocumento.objects.filter(nombre_documento__iexact=nombre_documento).first()

    @staticmethod
    def listar_por_grupo(grupo, investigacion=None):
        qs = TipoDocumento.objects.filter(grupo__iexact=grupo)
        if investigacion is not None:
            qs = qs.filter(investigacion=investigacion)
        return qs.order_by('nombre_documento')

    @staticmethod
    def existe_nombre(nombre_documento, excluir_id=None):
        qs = TipoDocumento.objects.filter(nombre_documento__iexact=nombre_documento)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()