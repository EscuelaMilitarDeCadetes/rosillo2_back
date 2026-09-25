from django.db import models

class TipoCalificacion(models.Model): 
    tipo_calificacion = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=150)
    evaluacion = models.BooleanField(default=False)
    orden_fase = models.IntegerField(db_column='ordenFase')

    def __str__(self):
        return self.tipo_calificacion