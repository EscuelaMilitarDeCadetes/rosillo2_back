from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class UsuarioService:

    @staticmethod
    def get_user_data(email):
        """
        Obtiene datos del usuario.
        """
        return get_object_or_404(User, email=email)

    @staticmethod
    def mostrar_todos_usuarios(activos=True):
        return User.objects.filter(is_active=activos)
    
    @staticmethod
    def obtener_persona_actual(user):
        """
        Retorna la Persona vinculada actualmente al Usuario.
        """
        asignacion = user.asignaciones.filter(estado=True).first()
        return asignacion.persona if asignacion else None        