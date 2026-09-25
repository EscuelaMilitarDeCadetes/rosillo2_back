from django.db import models
from django.conf import settings
from django.utils import timezone

class UsuarioXPersona(models.Model):
    """
    Modela la asignación de una Persona a una cuenta de Usuario en un período de tiempo.
    Esto permite que un Usuario (ej. 'coordinador_semillero@esmic.edu.co')
    sea utilizado por diferentes Personas a lo largo del tiempo, manteniendo un historial.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    persona = models.ForeignKey(
        'institucional.Persona',
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.BooleanField(default=True, help_text="Indica si esta es la asignación actualmente activa para el usuario.")

    class Meta:
        verbose_name = "Asignación de Usuario"
        verbose_name_plural = "Asignaciones de Usuario"
        ordering = ['-fecha_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario'],
                condition=models.Q(estado=True),
                name='unique_active_assignment_per_user'
            )
        ]

    def __str__(self):
        estado = "Activa" if self.estado else "Inactiva"
        return f'{self.usuario.username} -> {self.persona.nombre} {self.persona.apellido} ({estado})'