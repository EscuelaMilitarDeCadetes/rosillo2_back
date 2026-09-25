from django.db import models

class PuntoControl(models.Model): 
    control = models.CharField(max_length=255, unique=True)
    peso = models.FloatField(default=0)
    """
    Campo mantenido por compatibilidad con el sistema Thymeleaf.
    El avance oficial de un objetivo debe obtenerse del registro
    activo de ObjetivoXPunto y no de PuntoControl.completado.
    """
    completado = models.FloatField(default=0)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.control