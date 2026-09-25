from rest_framework import serializers

from apps.investigacion_formativa.models import ProcesoFormativo


class ProcesoFormativoSerializer(serializers.ModelSerializer):
    idea_nombre = serializers.SerializerMethodField()
    flujo_version_nombre = serializers.CharField(
        source='flujo_version.nombre',
        read_only=True
    )
    modalidad_nombre = serializers.SerializerMethodField()
    entidad_externa_nombre = serializers.SerializerMethodField()
    estado_actual = serializers.CharField(read_only=True)

    class Meta:
        model = ProcesoFormativo
        fields = '__all__'

    def get_idea_nombre(self, obj):
        if obj.idea is None:
            return None
        return obj.idea.idea

    def get_modalidad_nombre(self, obj):
        return obj.flujo_version.modalidad.nombre

    def get_entidad_externa_nombre(self, obj):
        if obj.entidad_externa is None:
            return None
        return obj.entidad_externa.nombre