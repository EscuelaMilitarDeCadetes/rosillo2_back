from django.db import models

class TipoRubro(models.Model): 
    nombre_rubro = models.CharField(max_length=50, unique=True)
    aplica = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_rubro