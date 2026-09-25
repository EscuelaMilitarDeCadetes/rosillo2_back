from django.db import models
from django.utils import timezone

class Gerente(models.Model):
    persona = models.ForeignKey("institucional.Persona", on_delete=models.CASCADE, null=True)
    fecha_ingreso = models.DateField(default=timezone.now)
    fecha_salida = models.DateField(null=True, blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        if self.persona:
            return f"Gerente: {self.persona.nombre} {self.persona.apellido}"
        return f"Gerente ID: {self.pk} (sin persona)"