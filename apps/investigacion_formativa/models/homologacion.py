from django.db import models

class Homologacion(models.Model):
    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente de aprobación"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
    ]
    proceso = models.OneToOneField("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE, related_name="homologacion")    
    acta_homologacion = models.ForeignKey("common.DocumentoFirma", null=True, blank=True, on_delete=models.SET_NULL, help_text="Acta formal de reconocimiento académico")
    aprobado_por = models.ForeignKey("usuarios.Usuario", null=True, blank=True, on_delete=models.SET_NULL, related_name="homologaciones_aprobadas")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="PENDIENTE")
    fecha_homologacion = models.DateField(null=True, blank=True)
    creditos_reconocidos = models.FloatField(null=True, blank=True, help_text="Créditos académicos reconocidos al homologar")
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Homologación"
        verbose_name_plural = "Homologaciones"
        
    def __str__(self):
        return f"Homologación de {self.proceso.titulo} [{self.get_estado_display()}]"