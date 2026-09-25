from django.db import models
from django.utils import timezone

class DocumentoFirmante(models.Model):

    ESTADO_FIRMA = [
        ("PENDIENTE", "Pendiente"),
        ("ACEPTADO", "Aceptado"),
        ("RECHAZADO", "Rechazado"),
        ("FIRMADO", "Firmado"),
    ]
    documento_firma = models.ForeignKey("common.DocumentoFirma", on_delete=models.CASCADE)
    usuario = models.ForeignKey("usuarios.Usuario", on_delete=models.CASCADE)
    orden = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_FIRMA, default="PENDIENTE")
    motivo_rechazo = models.TextField(blank=True, null=True)
    ip_firma = models.GenericIPAddressField()
    ruta_firma = models.CharField(max_length=255)
    codigo_verificacion = models.CharField(max_length=6, blank=True, null=True)
    fecha_firma = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('documento_firma', 'usuario')

    def __str__(self):
        return f"{self.usuario.username} - {self.documento_firma.tipo_documento.nombre_documento} - Versión {self.documento_firma.version}"