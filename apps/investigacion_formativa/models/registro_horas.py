from django.db import models

class RegistroHoras(models.Model):
    proceso = models.ForeignKey("investigacion_formativa.ProcesoFormativo", on_delete=models.CASCADE, related_name="control_horas")
    horas_requeridas = models.FloatField(default=120, help_text="Horas mínimas exigidas por la modalidad")
    horas_acumuladas = models.FloatField(default=0, help_text="Suma de horas validadas hasta la fecha")
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    cumple_requisito = models.BooleanField(default=False, help_text="True cuando horas_acumuladas >= horas_requeridas")
    
    def actualizar(self):
        total = (
            self.proceso.registros_actividades
            .aggregate(total=models.Sum('horas_reportadas'))
            .get('total') or 0
        )
        self.horas_acumuladas = total
        self.cumple_requisito = total >= self.horas_requeridas
        self.save()
        
    class Meta:
        verbose_name = "Control de Horas"
        verbose_name_plural = "Control de Horas"
        
    def __str__(self):
        return (f"{self.proceso.titulo} — " f"{self.horas_acumuladas}/{self.horas_requeridas} h")