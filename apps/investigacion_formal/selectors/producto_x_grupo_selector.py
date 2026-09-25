from apps.investigacion_formal.models import ProductoXGrupo


class ProductoXGrupoSelector:

    @staticmethod
    def listar():
        return (
            ProductoXGrupo.objects
            .select_related('producto_minciencias', 'grupo_minciencias', 'tipo_producto')
            .all()
        )

    @staticmethod
    def obtener(producto_x_grupo_id):
        return (
            ProductoXGrupo.objects
            .select_related('producto_minciencias', 'grupo_minciencias', 'tipo_producto')
            .get(pk=producto_x_grupo_id)
        )

    @staticmethod
    def existe(producto_x_grupo_id):
        return ProductoXGrupo.objects.filter(pk=producto_x_grupo_id).exists()

    @staticmethod
    def obtener_por_producto_minciencias(producto_minciencias_id):
        """Equivalente a getProductosXGrupo(id) del repo original."""
        return (
            ProductoXGrupo.objects
            .select_related('grupo_minciencias', 'tipo_producto')
            .filter(producto_minciencias_id=producto_minciencias_id)
            .first()
        )

    @staticmethod
    def listar_por_grupo_minciencias(grupo_minciencias_id):
        return (
            ProductoXGrupo.objects
            .select_related('producto_minciencias', 'tipo_producto')
            .filter(grupo_minciencias_id=grupo_minciencias_id)
        )

    @staticmethod
    def listar_por_tipo_producto(tipo_producto_id):
        return (
            ProductoXGrupo.objects
            .select_related('producto_minciencias', 'grupo_minciencias')
            .filter(tipo_producto_id=tipo_producto_id)
        )

    @staticmethod
    def existe_combinacion(producto_minciencias_id, grupo_minciencias_id, tipo_producto_id, excluir_id=None):
        """Refleja el unique_together del modelo: (producto_minciencias, grupo_minciencias, tipo_producto)."""
        qs = ProductoXGrupo.objects.filter(
            producto_minciencias_id=producto_minciencias_id,
            grupo_minciencias_id=grupo_minciencias_id,
            tipo_producto_id=tipo_producto_id,
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()