from rest_framework import serializers
from apps.usuarios.models import RolPlataforma
from apps.usuarios.constants import tipo_vinculacion


class RolPlataformaSerializer(serializers.ModelSerializer):
    """
    tipo_vinculacion / requiere_vinculacion: campos calculados.
    Le evitan al frontend mantener su propia copia de ROLES_CON_FACULTAD/
    ROLES_CON_GRUPO — ver AddRoleModal.js y ReemplazarUsuarioModal.js.
    """
    tipo_vinculacion = serializers.SerializerMethodField()
    requiere_vinculacion = serializers.SerializerMethodField()

    class Meta:
        model = RolPlataforma
        fields = ['id', 'nombre_rol', 'descripcion', 'tipo_vinculacion', 'requiere_vinculacion']

    def get_tipo_vinculacion(self, obj):
        return tipo_vinculacion(obj.nombre_rol)

    def get_requiere_vinculacion(self, obj):
        return tipo_vinculacion(obj.nombre_rol) is not None