from rest_framework import serializers
from apps.institucional.models import RolGrupo


class RolGrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolGrupo
        fields = '__all__'