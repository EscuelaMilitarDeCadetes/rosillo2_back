from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class DocumentoFirma(models.Model):

    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador"),
        ("EN_FIRMAS", "En proceso de firmas"),
        ("RECHAZADO", "Rechazado"),
        ("FIRMADO", "Firmado completamente"),
    ]
    tipo_documento = models.ForeignKey('common.TipoDocumento', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')
    version = models.IntegerField()
    ruta_documento = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="BORRADOR")
    hash_documento = models.CharField(max_length=64)
    ip_creacion = models.GenericIPAddressField()
    habilitado_firma = models.BooleanField(default=False)
    integridad_ok = models.BooleanField(null=True, default=None)
    fecha_ultima_verificacion_integridad = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('tipo_documento', 'content_type', 'object_id', 'version')
        indexes = [models.Index(fields=['content_type', 'object_id'])]

    def __str__(self):
        return f"{self.tipo_documento.nombre_documento} - Versión {self.version}"