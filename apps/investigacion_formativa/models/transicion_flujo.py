from django.db import models

class TransicionFlujo(models.Model):
    etapa_origen = models.ForeignKey("investigacion_formativa.EtapaFlujo", on_delete=models.CASCADE, related_name="origen")
    etapa_destino = models.ForeignKey("investigacion_formativa.EtapaFlujo", on_delete=models.CASCADE, related_name="destino")
    nombre = models.CharField(max_length=100, help_text="Nombre descriptivo de la transición (ej. 'Aprobación de propuesta')")
    condicion = models.TextField(blank=True, null=True, help_text="Expresión lógica o referencia a una ReglaFlujo para que la transición sea válida (ej. 'ReglaFlujo.id=1 AND ProcesoFormativo.nota >= 3.5')")
    accion_automatica = models.CharField(max_length=100, blank=True, null=True, help_text="Acción a ejecutar al realizar la transición (ej. 'ENVIAR_EMAIL', 'CREAR_TAREA', 'CAMBIAR_ESTADO_PROYECTO_FORMAL')")
    orden = models.IntegerField(default=0, help_text="Orden de evaluación de las transiciones si hay múltiples desde una etapa.")
    activo = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('etapa_origen', 'etapa_destino')
        verbose_name = "Transición de Flujo"
        verbose_name_plural = "Transiciones de Flujo"
        ordering = ['etapa_origen', 'orden']

    def __str__(self):
        return f"{self.etapa_origen} -> {self.etapa_destino}"