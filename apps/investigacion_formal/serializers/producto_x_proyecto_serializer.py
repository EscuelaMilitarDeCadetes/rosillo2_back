from rest_framework import serializers

from apps.investigacion_formal.models import ProductoXProyecto


class ProductoXProyectoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='producto_x_grupo.producto_minciencias.nombre_producto',
        read_only=True
    )
    producto_nomenclatura = serializers.CharField(
        source='producto_x_grupo.producto_minciencias.nomenclatura',
        read_only=True
    )
    grupo_nombre = serializers.CharField(
        source='producto_x_grupo.grupo_minciencias.nombre_grupo_minciencias',
        read_only=True
    )
    proyecto_titulo = serializers.CharField(
        source='proyecto.titulo',
        read_only=True
    )

    class Meta:
        model = ProductoXProyecto
        fields = '__all__'