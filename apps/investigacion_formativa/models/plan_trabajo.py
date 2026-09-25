from django.db import models

class PlanTrabajo(models.Model):
    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador"),
        ("ENVIADO", "Enviado a revisión"),
        ("APROBADO", "Aprobado"),
        ("RECHAZADO", "Rechazado"),
        ("ELIMINADO", "Eliminado"),
    ]
    proceso = models.OneToOneField("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE, related_name="plan_trabajo")
    aprobado_por = models.ForeignKey("usuarios.Usuario", on_delete=models.SET_NULL, null=True, blank=True, related_name="planes_aprobados")
    descripcion_general = models.TextField(help_text="Descripción general del trabajo o proyecto a desarrollar")
    objetivo_general = models.TextField()
    actividades_planeadas = models.TextField(help_text="Lista de actividades con cronograma estimado")
    fecha_inicio_planeada = models.DateField()
    fecha_fin_planeada = models.DateField()
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="BORRADOR")    
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Plan de Trabajo"
        verbose_name_plural = "Planes de Trabajo"
        
    def __str__(self):
        return f"Plan de trabajo — {self.proceso.titulo}"