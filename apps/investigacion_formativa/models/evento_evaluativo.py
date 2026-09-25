from django.db import models

class EventoEvaluativo(models.Model):
    proceso_formativo = models.ForeignKey("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE, related_name="sustentacion")
    acta_sustentacion = models.ForeignKey("common.DocumentoFirma", null=True, blank=True, on_delete=models.SET_NULL)    
    numero = models.IntegerField()
    es_obligatoria = models.BooleanField()
    fecha_sustentacion = models.DateTimeField()
    lugar = models.CharField(max_length=255, help_text="Ej: 'Sala de Juntas A' o 'Virtual vía Teams'")
    resultado = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sustentación de Proceso de Grado"
        verbose_name_plural = "Sustentaciones de Proceso de Grado"
        unique_together = ('proceso_formativo', 'acta_sustentacion')

    def __str__(self):
        return f"Sustentación de {self.proceso_formativo.titulo} - {self.resultado}"