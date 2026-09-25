from django.db import models

class ParticipanteProceso(models.Model):
    ROLES_PARTICIPANTE = [
        ('ESTUDIANTE', 'Estudiante'),
        ('TUTOR', 'Tutor'),
        ('JURADO', 'Jurado'),
        ('INVESTIGADOR_PRINCIPAL', 'Investigador Principal'),
        ('COORDINADOR', 'Coordinador'),
        ('OTRO', 'Otro'),
    ]
    
    proceso_formativo = models.ForeignKey('investigacion_formativa.ProcesoFormativo', on_delete=models.CASCADE, related_name='participantes')
    persona = models.ForeignKey('institucional.Persona', on_delete=models.PROTECT)
    rol_en_modalidad = models.CharField(max_length=50, choices=ROLES_PARTICIPANTE)
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_finalizacion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Participante de Modalidad"
        verbose_name_plural = "Participantes de Modalidad"
        unique_together = ('proceso_formativo', 'persona')
        
    def __str__(self):
        return f"{self.persona.nombre} {self.persona.apellido} - {self.rol_en_modalidad}"