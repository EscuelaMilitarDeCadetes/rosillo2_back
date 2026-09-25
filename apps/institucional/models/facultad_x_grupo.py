from django.db import models

class FacultadXGrupo(models.Model):
    grupo = models.ForeignKey("institucional.GrupoInvestigacion", on_delete=models.CASCADE, null=True, blank=True)
    facultad = models.ForeignKey("institucional.FacultadEscuela", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('grupo', 'facultad')
    
    def __str__(self):
        return f"{self.grupo} - {self.facultad}"