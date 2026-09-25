from django.db import models

class Persona(models.Model):
    grado = models.ForeignKey("institucional.GradoEstudios", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80)
    documento = models.CharField(max_length=20, unique=True)
    celular = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(max_length=150, unique=True)
    cvlac = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f'{self.grado} {self.nombre} {self.apellido}'