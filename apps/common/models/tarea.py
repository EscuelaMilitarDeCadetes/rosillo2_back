from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Tarea(models.Model):
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tareas')
    descripcion = models.CharField(max_length=255)
    completada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)
    
    # Para vincular a CUALQUIER objeto: un Proyecto, una Tesis, un DocumentoFirma, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.descripcion