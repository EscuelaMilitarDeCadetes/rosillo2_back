from apps.investigacion_formal.models import TipoProducto


class TipoProductoSelector:

    @staticmethod
    def listar():
        return TipoProducto.objects.all().order_by('tipo_producto')

    @staticmethod
    def obtener(tipo_producto_id):
        return TipoProducto.objects.get(pk=tipo_producto_id)

    @staticmethod
    def existe(tipo_producto_id):
        return TipoProducto.objects.filter(pk=tipo_producto_id).exists()

    @staticmethod
    def existe_nombre(tipo_producto, excluir_id=None):
        qs = TipoProducto.objects.filter(tipo_producto__iexact=tipo_producto)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()