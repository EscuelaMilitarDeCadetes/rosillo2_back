from django.db import models

class GradoEstudios(models.Model):
    sigla_grado = models.CharField(max_length=3, unique=True)
    descripcion = models.CharField(max_length=150)

    def __str__(self):
        return self.sigla_grado