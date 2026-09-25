from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.common.services.historial_service import HistorialService


@receiver(post_delete, sender='usuarios.RolXUsuario')
def rol_x_usuario_eliminado(sender, instance, **kwargs):
    HistorialService.registrar(
        ejecutor=None,
        descripcion=(
            f"[SISTEMA] Eliminación física del rol "
            f"'{instance.rol.nombre_rol}' "
            f"del usuario '{instance.usuario.username}'"
        )
    )