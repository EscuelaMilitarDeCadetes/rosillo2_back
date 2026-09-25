"""
Selector de integración.

Lee datos transversales que cruzan usuarios e institucional.
Solo lectura — no escribe en ninguna tabla.
"""
from django.contrib.auth import get_user_model
from apps.usuarios.models import RolXUsuario, UsuarioXPersona

User = get_user_model()


class VinculacionSelector:

    @staticmethod
    def obtener_persona_usuario(usuario_id: int):
        """Devuelve la Persona activa asignada al usuario, o None."""
        asignacion = (
            UsuarioXPersona.objects
            .select_related('persona')
            .filter(usuario_id=usuario_id, estado=True)
            .first()
        )
        return asignacion.persona if asignacion else None

    @staticmethod
    def obtener_rol_plataforma(usuario_id: int):
        """Devuelve el primer RolPlataforma activo del usuario, o None."""
        rxu = (
            RolXUsuario.objects
            .select_related('rol')
            .filter(usuario_id=usuario_id, estado=True)
            .first()
        )
        return rxu.rol if rxu else None

    @staticmethod
    def usuario_activo(usuario_id: int) -> bool:
        return User.objects.filter(pk=usuario_id, is_active=True).exists()