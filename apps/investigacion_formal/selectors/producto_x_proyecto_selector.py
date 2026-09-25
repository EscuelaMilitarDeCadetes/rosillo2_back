from apps.investigacion_formal.models import ProductoXProyecto


class ProductoXProyectoSelector:

    @staticmethod
    def listar():
        return (
            ProductoXProyecto.objects
            .select_related('producto_x_grupo', 'proyecto')
            .all()
        )

    @staticmethod
    def obtener(producto_x_proyecto_id):
        return (
            ProductoXProyecto.objects
            .select_related('producto_x_grupo', 'proyecto')
            .get(pk=producto_x_proyecto_id)
        )

    @staticmethod
    def listar_por_proyecto(proyecto_id, solo_activos=True):
        """Equivalente a findByTituloProyectoFk / getDocumentosXProductosXProyecto."""
        qs = (
            ProductoXProyecto.objects
            .select_related('producto_x_grupo')
            .filter(proyecto_id=proyecto_id)
        )
        if solo_activos:
            qs = qs.filter(activo=True)
        return qs

    @staticmethod
    def listar_pendientes_por_proyecto(proyecto_id):
        """Equivalente a getProductosByIdproyecto(id): entregado=false AND activo=true."""
        return (
            ProductoXProyecto.objects
            .select_related('producto_x_grupo', 'producto_x_grupo__producto_minciencias')
            .filter(proyecto_id=proyecto_id, entregado=False, activo=True)
        )

    @staticmethod
    def listar_entregados_por_proyecto(proyecto_id):
        return (
            ProductoXProyecto.objects
            .select_related('producto_x_grupo')
            .filter(proyecto_id=proyecto_id, entregado=True, activo=True)
        )

    @staticmethod
    def existe_combinacion(producto_x_grupo_id, proyecto_id, excluir_id=None):
        qs = ProductoXProyecto.objects.filter(
            producto_x_grupo_id=producto_x_grupo_id,
            proyecto_id=proyecto_id,
        )
        if excluir_id is not None:
            qs = qs.exclude(pk=excluir_id)
        return qs.exists()