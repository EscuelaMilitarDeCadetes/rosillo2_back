from django.db import models

class Tutor(models.Model):
    persona = models.OneToOneField('institucional.Persona', on_delete=models.CASCADE)
    facultad = models.ForeignKey('institucional.FacultadEscuela', on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"
        unique_together = ('persona', 'facultad')        

    def __str__(self):
        return f"Tutor: {self.persona.nombre} {self.persona.apellido}"