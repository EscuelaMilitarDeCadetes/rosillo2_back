from django.db import models

class ActividadFormativa(models.Model):
    ESTADOS_ACTIVIDAD = [
        ('PLANIFICADA', 'Planificada'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('ELIMINADA', 'Eliminada'),
    ]
    
    proceso_formativo = models.ForeignKey('investigacion_formativa.ProcesoFormativo', on_delete=models.CASCADE, related_name='actividades_formativas')
    documento_soporte = models.ForeignKey('common.DocumentoFirma', on_delete=models.SET_NULL, null=True, blank=True, help_text="Documento que soporta la realización de la actividad (ej. reporte, certificado).")
    responsable = models.ForeignKey('institucional.Persona', on_delete=models.PROTECT, help_text="Persona responsable de la ejecución o reporte de la actividad.")
    nombre = models.CharField(max_length=255, help_text="Nombre de la actividad (ej. 'Seguimiento Mensual', 'Participación en Evento').")
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    horas_dedicadas = models.IntegerField(null=True, blank=True, help_text="Horas dedicadas a esta actividad.")
    estado = models.CharField(max_length=50, choices=ESTADOS_ACTIVIDAD, default='PLANIFICADA')    
    
    class Meta:
        verbose_name = "Actividad Formativa"
        verbose_name_plural = "Actividades Formativas"
        
    def __str__(self):
        return self.nombre