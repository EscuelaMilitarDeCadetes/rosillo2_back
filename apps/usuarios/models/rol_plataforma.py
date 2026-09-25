from django.db import models

class RolPlataforma(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=180)

    def __str__(self):
        return self.nombre_rol