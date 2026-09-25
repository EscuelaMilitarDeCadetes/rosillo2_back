from django.db import models

class ProyectoXConvocatoria(models.Model):
    convocatoria = models.ForeignKey("investigacion_formal.Convocatoria", on_delete=models.CASCADE)
    proyecto = models.ForeignKey("investigacion_formal.Proyecto", on_delete=models.CASCADE)
    estado = models.BooleanField()
    estado_finalizado_calificacion = models.BooleanField(default=False)
    ultimo_filtro_calificacion = models.CharField(max_length=255, null=True, blank=True)
    aprobacion_ultima_calificacion = models.BooleanField(default=False)
    calificacion_ultimo_filtro_calificacion = models.CharField(max_length=255, null=True, blank=True)
    modificacion_documento_proyecto = models.BooleanField(default=False)

    class Meta:
        unique_together = ('convocatoria', 'proyecto')
    
    def __str__(self):
        return f"{self.convocatoria} - {self.proyecto}"