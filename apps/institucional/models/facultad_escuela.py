from django.db import models

class FacultadEscuela(models.Model): 
    nombre_facultad = models.CharField(max_length=30, unique=True)
    abreviatura = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.nombre_facultad