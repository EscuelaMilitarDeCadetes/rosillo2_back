from django.db import models

class Revision(models.Model):
    instancia_etapa = models.ForeignKey("investigacion_formativa.InstanciaEtapa", on_delete=models.CASCADE)
    version = models.IntegerField()
    observaciones = models.TextField()
    aprobado = models.BooleanField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('instancia_etapa', 'version')
        verbose_name = "Revisión"
        verbose_name_plural = "Revisión"

    def __str__(self):
        return f"Revisión {self.version}"