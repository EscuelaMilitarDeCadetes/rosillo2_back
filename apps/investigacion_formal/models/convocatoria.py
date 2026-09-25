from django.db import models

class Convocatoria(models.Model):
    nombre_convocatoria = models.CharField(max_length=200, unique=True)
    anio_convocatoria = models.IntegerField()
    inicio = models.DateField()
    cierre = models.DateField()
    estado = models.BooleanField(default=True)
    interno = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_convocatoria