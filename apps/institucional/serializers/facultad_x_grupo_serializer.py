from rest_framework import serializers
from apps.institucional.models import FacultadXGrupo


class FacultadXGrupoSerializer(serializers.ModelSerializer):
    grupo_nombre = serializers.CharField(
        source='grupo.sigla_grupo',
        read_only=True
    )
    facultad_nombre = serializers.CharField(
        source='facultad.abreviatura',
        read_only=True
    )

    class Meta:
        model = FacultadXGrupo
        fields = '__all__'