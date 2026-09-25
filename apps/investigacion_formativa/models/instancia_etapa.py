from django.db import models

class InstanciaEtapa(models.Model):
        
    proceso = models.ForeignKey("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE)
    etapa = models.ForeignKey("investigacion_formativa.EtapaFlujo", on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=20,
        choices=[
            ("PENDIENTE", "Pendiente"),
            ("EN_PROCESO", "En Proceso"),
            ("APROBADO", "Aprobado"),
            ("RECHAZADO", "Rechazado"),
            ("SEGUNDA_INSTANCIA", "Segunda Instancia")
        ]
    )
    fecha_inicio = models.DateTimeField(null=True)
    fecha_fin = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('proceso', 'etapa')

    def __str__(self):
        return f"Instancia de Etapa: {self.etapa.nombre}"