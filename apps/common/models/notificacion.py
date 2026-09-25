from django.db import models

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('info', 'Información'),
        ('exito', 'Éxito'),
        ('alerta', 'Alerta'),
        ('error', 'Error'),
    ]
    usuario_destino = models.ForeignKey("usuarios.Usuario", on_delete=models.CASCADE)
    mensaje = models.TextField()
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        blank=True,
        null=True,
    )
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    url_relacionada = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.mensaje