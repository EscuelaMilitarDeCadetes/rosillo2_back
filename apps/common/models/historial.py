from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Historial(models.Model): 
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    accion = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Historial"
        verbose_name_plural = "Historial"

    def __str__(self):
        usuario = self.usuario.username if self.usuario else "SISTEMA"
        return f"{usuario} - {self.accion}"