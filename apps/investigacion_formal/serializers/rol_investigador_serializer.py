from rest_framework import serializers

from apps.investigacion_formal.models import RolInvestigador


class RolInvestigadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolInvestigador
        fields = '__all__'