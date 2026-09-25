from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

class IndicadorImpacto(models.Model):
    proyecto = models.ForeignKey('investigacion_formal.Proyecto', on_delete=models.CASCADE)
    kpi_nombre = models.CharField(max_length=100) 
    valor_proyectado = models.FloatField()
    valor_real = models.FloatField(default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Indicador de Impacto"
        verbose_name_plural = "Indicadores de Impacto"
        constraints = [
            UniqueConstraint(
                Lower("kpi_nombre"),
                "proyecto",
                name="uq_indicador_proyecto_kpi_lower",
            )
        ]
        ordering = ['-ultima_actualizacion']
    
    def __str__(self):
        return f"{self.proyecto.titulo} - {self.kpi_nombre}"