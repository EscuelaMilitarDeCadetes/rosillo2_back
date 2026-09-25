from django.db import models

class RolInvestigador(models.Model):
    nombre_rol_investigador = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_rol_investigador