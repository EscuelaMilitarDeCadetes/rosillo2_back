from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


def validar_fortaleza_password(value, user=None):
    """
    Validador reutilizable de DRF que delega en los AUTH_PASSWORD_VALIDATORS
    configurados en settings, para no duplicar reglas entre serializers.
    """
    try:
        validate_password(value, user=user)
    except DjangoValidationError as e:
        raise serializers.ValidationError(e.messages)
    return value