from django.db import models


class Interaccion(models.Model):
    entidad = models.ForeignKey("crm.EntidadExterna", on_delete=models.CASCADE)
    proyecto_asociado = models.ForeignKey('investigacion_formal.Proyecto', null=True, on_delete=models.SET_NULL)
    fecha = models.DateTimeField(auto_now_add=True)
    medio = models.CharField(max_length=50, choices=[('REUNION', 'Reunión'), ('CONVENIO', 'Firma Convenio')])
    resumen = models.TextField()

    class Meta:
        verbose_name = "Interacción"
        verbose_name_plural = "Interacciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.entidad} - {self.fecha}"