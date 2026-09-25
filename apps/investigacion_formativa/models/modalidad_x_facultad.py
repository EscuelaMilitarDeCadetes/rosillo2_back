from django.db import models

class ModalidadXFacultad(models.Model):
    facultad = models.ForeignKey("institucional.FacultadEscuela", on_delete=models.CASCADE)
    modalidad = models.ForeignKey("investigacion_formativa.Modalidad", on_delete=models.CASCADE)
    disponible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('facultad', 'modalidad')
    
    def __str__(self):
        return f"{self.facultad.nombre_facultad} - {self.modalidad.nombre}"