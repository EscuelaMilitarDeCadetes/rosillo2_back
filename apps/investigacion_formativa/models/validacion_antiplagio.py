from django.db import models

class ValidacionAntiplagio(models.Model):
    instancia_etapa = models.ForeignKey("investigacion_formativa.InstanciaEtapa", on_delete=models.CASCADE)
    documento = models.ForeignKey("common.DocumentoFirma", on_delete=models.CASCADE)
    porcentaje = models.FloatField()
    aprobado = models.BooleanField()
    
    class Meta:
        unique_together = ('instancia_etapa', 'documento')
        verbose_name = "Validación de Antiplagio"
        verbose_name_plural = "Validaciones de Antiplagio"

    def __str__(self):
        return f"Antiplagio {self.porcentaje}% - {self.documento.tipo_documento.nombre_documento}"