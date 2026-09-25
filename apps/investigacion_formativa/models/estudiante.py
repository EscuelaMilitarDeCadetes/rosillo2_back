from django.db import models

class Estudiante(models.Model):
    persona = models.OneToOneField('institucional.Persona', on_delete=models.CASCADE)
    modalidad_facultad = models.ForeignKey("investigacion_formativa.ModalidadXFacultad", on_delete=models.CASCADE)
    correo_personal = models.EmailField(max_length=150)
    nivel = models.CharField(max_length=50)
    estado = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"    

    def __str__(self):
        return f"Estudiante: {self.persona.nombre} {self.persona.apellido}" 