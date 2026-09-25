from django.db import models

class Calificacion(models.Model):
    fase = models.ForeignKey("investigacion_formal.TipoCalificacion", on_delete=models.CASCADE)
    aplicar = models.ForeignKey("investigacion_formal.ProyectoXConvocatoria", on_delete=models.CASCADE)
    observacion = models.CharField(max_length=1000)
    aprobado = models.BooleanField(default=False)
    primer_sin_observacion = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fase} - {self.aplicar}"

    class Meta:
        unique_together = ('fase', 'aplicar')