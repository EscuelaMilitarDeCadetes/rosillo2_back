from django.db import models

class SegundaInstancia(models.Model):
    proceso = models.OneToOneField("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE)
    instancia_etapa = models.ForeignKey("investigacion_formativa.InstanciaEtapa", on_delete=models.CASCADE)
    evaluacion = models.ForeignKey("investigacion_formativa.EvaluacionProceso", on_delete=models.CASCADE)
    etapa_retorno = models.ForeignKey("investigacion_formativa.EtapaFlujo", on_delete=models.CASCADE)
    activada = models.BooleanField(default=False)
    consumida = models.BooleanField(default=False)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ("TUTOR", "Tutor"),
            ("JURADO", "Jurado"),
            ("SUSTENTACION", "Sustentación"),
            ("ANTIPLAGIO", "Antiplagio")
        ]
    )
    motivo = models.TextField()
    nota_maxima = models.FloatField(default=3.5)
    fecha_activacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Segunda Instancia"
        verbose_name_plural = "Segunda Instancia"     

    def __str__(self):
        return f"Segunda Instancia de {self.proceso.titulo}"