from django.db import models

class FlujoProceso(models.Model):
    TIPOS_FLUJO = [
        ('FORMATIVA', 'Investigación Formativa'),
        ('FORMAL', 'Investigación Formal'),
    ]
    modalidad = models.ForeignKey("investigacion_formativa.Modalidad", on_delete=models.CASCADE, related_name="flujos")
    nombre = models.CharField(max_length=150, unique=True, help_text="Nombre del flujo de proceso (ej. 'Flujo Trabajo de Grado Pregrado').")
    version = models.IntegerField(default=1)
    tipo = models.CharField(max_length=20, choices=TIPOS_FLUJO, default='FORMATIVA')
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_vigencia_inicio = models.DateField()
    fecha_vigencia_fin = models.DateField(null=True, blank=True)
    
    @property
    def modalidad_nombre(self):
        return self.modalidad.nombre
    
    class Meta:
        verbose_name = "Flujo de Proceso"
        verbose_name_plural = "Flujos de Proceso"
        unique_together = ('modalidad', 'version')
        ordering = ['modalidad', 'version']
        
    def __str__(self):
        return f"{self.modalidad.nombre} — v{self.version}"