from django.db import models

class Ejecucion(models.Model):
    monto = models.ForeignKey("investigacion_formal.Monto", on_delete=models.CASCADE)
    tipo_rubro = models.ForeignKey("investigacion_formal.TipoRubro", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    costo = models.FloatField(default=0)
    descripcion = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre