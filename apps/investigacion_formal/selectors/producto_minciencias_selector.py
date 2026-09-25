from apps.investigacion_formal.models import ProductoMinciencias


class ProductoMincienciasSelector:

    @staticmethod
    def listar():
        return ProductoMinciencias.objects.all().order_by('nombre_producto')

    @staticmethod
    def obtener(producto_minciencias_id):
        return ProductoMinciencias.objects.get(pk=producto_minciencias_id)

    @staticmethod
    def existe(producto_minciencias_id):
        return ProductoMinciencias.objects.filter(pk=producto_minciencias_id).exists()

    @staticmethod
    def existe_nombre(nombre_producto, excluir_id=None):
        qs = ProductoMinciencias.objects.filter(nombre_producto__iexact=nombre_producto)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()

    @staticmethod
    def existe_nomenclatura(nomenclatura, excluir_id=None):
        qs = ProductoMinciencias.objects.filter(nomenclatura__iexact=nomenclatura)
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()