from django.db import models

class Objetivos(models.Model):
    proyecto = models.ForeignKey("investigacion_formal.Proyecto", on_delete=models.CASCADE)
    objetivo = models.CharField(max_length=255, unique=True)
    clase = models.CharField(max_length=15, null=True, blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.objetivo