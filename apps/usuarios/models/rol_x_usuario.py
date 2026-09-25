from django.db import models
from django.conf import settings

class RolXUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roles_usuario')    
    rol = models.ForeignKey("usuarios.RolPlataforma", on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    class Meta:
        unique_together = ('usuario', 'rol')
        db_table = 'rol_x_usuario'

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre_rol}"