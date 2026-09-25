from django.db import models
from django.db.models import Q

class ObjetivoXPunto(models.Model):
    objetivo = models.ForeignKey("investigacion_formal.Objetivos", on_delete=models.CASCADE)
    punto_control = models.ForeignKey("investigacion_formal.PuntoControl", on_delete=models.CASCADE)
    descripcion_avance = models.CharField(max_length=255)
    avance = models.FloatField(default=0)
    mes_avance = models.CharField(max_length=20)
    anio_avance = models.IntegerField()
    estado = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['objetivo', 'punto_control'],
                condition=Q(estado=True),
                name='objetivo_x_punto_unico_activo',
            )
        ]
    
    def __str__(self):
        return f"{self.objetivo} - {self.punto_control}"