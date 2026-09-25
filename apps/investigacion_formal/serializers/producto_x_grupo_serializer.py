from rest_framework import serializers

from apps.investigacion_formal.models import ProductoXGrupo


class ProductoXGrupoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='producto_minciencias.nombre_producto',
        read_only=True
    )
    producto_nomenclatura = serializers.CharField(
        source='producto_minciencias.nomenclatura',
        read_only=True
    )
    grupo_nombre = serializers.CharField(
        source='grupo_minciencias.nombre_grupo_minciencias',
        read_only=True
    )
    tipo_producto_nombre = serializers.CharField(
        source='tipo_producto.tipo_producto',
        read_only=True
    )

    class Meta:
        model = ProductoXGrupo
        fields = '__all__'