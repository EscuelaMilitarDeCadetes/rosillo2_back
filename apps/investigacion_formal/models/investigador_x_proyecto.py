from django.db import models

class InvestigadorXProyecto(models.Model):
    rol_investigador = models.ForeignKey("investigacion_formal.RolInvestigador", on_delete=models.CASCADE)
    proyecto = models.ForeignKey("investigacion_formal.Proyecto", on_delete=models.CASCADE)
    persona_x_grupo = models.ForeignKey("institucional.PersonaXGrupo", on_delete=models.CASCADE)
    orcid = models.CharField(max_length=255, null=True, blank=True)
    estado = models.BooleanField(default=True)

    class Meta:
        unique_together = ('rol_investigador', 'proyecto', 'persona_x_grupo')
    
    def __str__(self):
        return f"{self.rol_investigador} - {self.proyecto} - {self.persona_x_grupo}"