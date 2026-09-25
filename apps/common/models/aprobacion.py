from django.db import models

class Aprobacion(models.Model):
    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADO", "Aprobado"),
        ("RECHAZADO", "Rechazado"),
    ]

    usuario_revisor = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.CASCADE
    )
    tipo_documento = models.ForeignKey(
        "common.TipoDocumento",
        on_delete=models.CASCADE
    )
    id_documento = models.IntegerField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
    )
    observacion = models.TextField(blank=True, null=True)
    fecha_revision = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario_revisor', 'tipo_documento', 'id_documento')

    def __str__(self):
        return f"{self.usuario_revisor.username} - {self.tipo_documento.nombre_documento} - {self.id_documento}"