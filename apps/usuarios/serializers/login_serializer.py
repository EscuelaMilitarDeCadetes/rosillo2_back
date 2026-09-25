from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    """
    Serializer para validar las credenciales de entrada en el login.
    """
    username = serializers.EmailField(
        required=True,
        error_messages={"invalid": "El formato del usuario debe ser un correo electrónico (ej. usuario@esmic.edu.co)."}
    )
    password = serializers.CharField(required=True, write_only=True)