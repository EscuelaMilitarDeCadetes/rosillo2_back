from django.db import models

class RequisitoModalidad(models.Model):
    modalidad = models.ForeignKey("investigacion_formativa.Modalidad", on_delete=models.CASCADE, related_name="requisitos")
    tipo = models.CharField(
        max_length=30,
        choices=[
            ("PROMEDIO_MINIMO", "Promedio académico mínimo"),
            ("HORAS_MINIMAS", "Horas mínimas requeridas"),
            ("PROYECTO_FORMAL", "Requiere vínculo con proyecto formal"),
            ("PRODUCTO_CTEI", "Requiere producto CTeI"),
            ("EVENTO_CIENTIFICO", "Requiere participación en evento"),
            ("CERTIFICADO_EXTERNO", "Requiere certificado externo"),
            ("OTRO", "Otro requisito"),
        ]
    )
    valor_numerico = models.FloatField(null=True, blank=True, help_text="Para promedio mínimo (ej: 3.8) o horas mínimas (ej: 120)")
    valor_booleano = models.BooleanField(null=True, blank=True, help_text="Para requisitos de tipo sí/no (ej: requiere proyecto formal)")
    descripcion = models.TextField(help_text="Descripción del requisito según el reglamento")
    activo = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('modalidad', 'tipo')
        verbose_name = "Requisito de Modalidad"
        verbose_name_plural = "Requisitos de Modalidad"
        
    def __str__(self):
        return f"{self.modalidad.nombre} - {self.get_tipo_display()}"