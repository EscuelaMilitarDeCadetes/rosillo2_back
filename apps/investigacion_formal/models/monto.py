from django.db import models

class Monto(models.Model):
    proyecto = models.ForeignKey("investigacion_formal.Proyecto", on_delete=models.CASCADE)
    solicitado = models.FloatField(default=0)
    aprobado = models.FloatField(null=True, blank=True)
    asignado = models.DateField(null=True, blank=True)
    ejecutado = models.FloatField(null=True, blank=True)
    contrapartida = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'Montos para {self.proyecto.titulo}'