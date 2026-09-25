from django.db import models

class EvaluacionProceso(models.Model):
    evaluador = models.ForeignKey("investigacion_formativa.ParticipanteProceso", on_delete=models.CASCADE, related_name="evaluaciones")  
    instancia_etapa = models.ForeignKey("investigacion_formativa.InstanciaEtapa", on_delete=models.CASCADE)
    concepto = models.CharField(max_length=100) 
    aprobado = models.BooleanField() 
    observaciones = models.TextField(blank=True, null=True)    
    nota = models.FloatField()
    tipo_evaluador = models.CharField(max_length=100)
    tipo_evaluacion = models.CharField(max_length=100)
    peso = models.FloatField()
    resultado = models.CharField(max_length=100)
    es_tercer_evaluador = models.BooleanField(default=False)
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)
    rubrica_evaluacion = models.CharField(max_length=100, blank=True)
    criterio_rubrica = models.CharField(max_length=100, blank=True)
    resultado_criterio = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Evaluación de Proceso de Grado"
        verbose_name_plural = "Evaluaciones de Proceso de Grado"
        unique_together = ('evaluador', 'instancia_etapa')

    def save(self, *args, **kwargs):
        # Lógica de negocio: En Segunda Instancia la nota máxima es 3.5
        from .segunda_instancia import SegundaInstancia
        
        proceso = self.instancia_etapa.proceso
        if SegundaInstancia.objects.filter(proceso=proceso, activa=True).exists():
            if self.nota > 3.5:
                self.nota = 3.5
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluación de {self.evaluador} - Concepto: {self.concepto}"