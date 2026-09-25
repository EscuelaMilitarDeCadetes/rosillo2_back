from rest_framework import serializers
from django_recaptcha.fields import ReCaptchaField
from .validators import validar_fortaleza_password


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    recaptcha = ReCaptchaField()

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        return validar_fortaleza_password(value)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # user se inyecta en la vista vía serializer.context, para que
        # UserAttributeSimilarityValidator compare contra username/email reales
        user = self.context.get('user')
        return validar_fortaleza_password(value, user=user)
