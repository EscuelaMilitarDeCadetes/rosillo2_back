from rest_framework import serializers

class SoporteSolicitudSerializer(serializers.Serializer):
    asunto = serializers.CharField(max_length=255)
    mensaje = serializers.CharField()